
from ROOT import TCanvas, TFile, gStyle

import numpy as np
from torchic import Dataset, AxisSpec
from torchic.core.histogram import build_efficiency
from torchic.utils.root import set_root_object
from torchic.physics.ITS import average_cluster_size

import argparse


import sys
sys.path.append('../../')
from utils.particles import ParticlePDG, ParticleMasses, ParticleLabels

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Calculate efficiency for nucleiSpectra')
    parser.add_argument('--input', type=str, default='output/aod/LHC25a3_030426.root', help='Input ROOT file')
    parser.add_argument('--output', type=str, default='output/efficiency/efficiency', help='Output ROOT file')
    #parser.add_argument('--pdg', type=int, default=1000020030, help='PDG code of the particle to analyze (default: 1000020030 for He3)')
    args = parser.parse_args()
    
    gStyle.SetOptStat(0)
    suffix = ''
    
    dataset = Dataset.from_root(args.input, 'O2nuctablemcsel', 'DF*')
    print(dataset.columns)
    
    read_bit_from_flags =  lambda x, indexbit: (x >> indexbit) & 0b1

    dataset['fFlags_bit0'] = dataset['fFlags'].apply(read_bit_from_flags, args=(0,))
    dataset['fFlags_bit9'] = dataset['fFlags'].apply(read_bit_from_flags, args=(9,))
    dataset['fFlags_bit10'] = dataset['fFlags'].apply(read_bit_from_flags, args=(10,))
    dataset['fFlags_bit11'] = dataset['fFlags'].apply(read_bit_from_flags, args=(11,))

    dataset.query('fFlags_bit9 == 1', inplace=True)
    #dataset.query('fFlags_bit10 == 0', inplace=True)
    #dataset.query('fFlags_bit11 == 0', inplace=True)
    dataset['fgEventMask_bit3'] = dataset['fgEventMask'].apply(read_bit_from_flags, args=(3,))
    dataset.query('fgEventMask_bit3 == 1', inplace=True) # select particles from reconstructed events
    
    print(dataset['fPDGcode'].unique())
    for particle in ['He', 'Pr']:
        
        prepath = '/'.join(args.output.split('/')[:-1])
        output_path =  prepath + '/' + particle + '/' + args.output.split('/')[-1]
        
        pdg = ParticlePDG[particle]
        mass = ParticleMasses[particle]
        charge = 2 if particle == 'He' else 1
        PT_MAX = 10 if particle == 'He' else 5

        particle_dataset = dataset.query(f'abs(fPDGcode) == {pdg}', inplace=False)
        
        particle_dataset['fgP'] = particle_dataset['fgPt'] * np.cosh(particle_dataset['fgEta'])
        particle_dataset['fgPz'] = particle_dataset['fgPt'] * np.sinh(particle_dataset['fgEta'])
        particle_dataset['fgE'] = np.sqrt(particle_dataset['fgP']**2 + mass**2)
        particle_dataset['fgY'] = 0.5 * np.log((particle_dataset['fgE'] + particle_dataset['fgPz']) / (particle_dataset['fgE'] - particle_dataset['fgPz']))
        #particle_dataset.query(f'(abs(fgY) < 0.5) or fPt > 900', inplace=True)

        particle_dataset['fSign'] = particle_dataset['fPDGcode'].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)

        particle_dataset['fPt'] = particle_dataset['fPt'] * charge
        particle_dataset['fSignedPt'] = particle_dataset['fPt'] #* particle_dataset['fSign']
        particle_dataset['fgSignedPt'] = particle_dataset['fgPt'] * particle_dataset['fSign']

        h_num = particle_dataset.build_th1('fSignedPt', AxisSpec(40, -PT_MAX, PT_MAX, 'Recontructed', 'Recontructed;#it{p}_{T} (GeV/c)'))
        set_root_object(h_num, line_color=2, marker_color=2, marker_style=20) 
        h_den = particle_dataset.build_th1('fgSignedPt', AxisSpec(40, -PT_MAX, PT_MAX, 'Generated', 'Generated;#it{p}_{T} (GeV/c)'))

        h_eta = particle_dataset.build_th1('fgEta', AxisSpec(100, -5, 5, 'gen_eta'))
        h_y = particle_dataset.build_th1('fgY', AxisSpec(100, -5, 5, 'gen_y'))
        h_dcaxy = particle_dataset.build_th1('fDCAxy', AxisSpec(200, -0.5, 0.5, ';DCA_{xy} (cm);'))
        h_dcaz = particle_dataset.build_th1('fDCAz', AxisSpec(200, -0.5, 0.5, ';DCA_{z} (cm);'))
        
        h_eff = build_efficiency(h_den, h_num, name='nucleiSpectra', xtitle='#it{p}_{T} (GeV/#it{c})', ytitle='#varepsilon')

        canvas = TCanvas()
        hframe = canvas.DrawFrame(-PT_MAX, 0, PT_MAX, h_den.GetMaximum() * 1.2, f'nucleiSpectra;{h_den.GetXaxis().GetTitle()};{h_den.GetYaxis().GetTitle()}')
        h_den.Draw('hist same')
        h_num.Draw('hist same')
        canvas.BuildLegend()
        canvas.SaveAs(f'{output_path}pt.pdf')

        canvas.Clear()
        canvas.DrawFrame(-PT_MAX, 0, PT_MAX, 1.2, f'{h_eff.GetTitle()};{h_eff.GetXaxis().GetTitle()};{h_eff.GetYaxis().GetTitle()}')
        h_eff.Draw('E same')
        canvas.SaveAs(f'{output_path}.pdf')

        outfile = TFile(f'{output_path}.root', 'RECREATE')
        h_num.Write('numerator')
        h_den.Write('denominator')
        h_eff.Write('efficiency')
        h_eta.Write('gen_eta')
        h_y.Write('gen_y')
        outfile.Close()
        
        for hist in [h_num, h_den, h_eff, h_eta, h_y, h_dcaxy, h_dcaz]:
            del hist

