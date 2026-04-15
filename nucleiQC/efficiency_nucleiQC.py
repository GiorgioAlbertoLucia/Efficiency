
from ROOT import TCanvas, TFile, gStyle


from torchic import Dataset, AxisSpec
from torchic.core.histogram import build_efficiency
from torchic.utils.root import set_root_object


import argparse

import sys
sys.path.append('../../')
from torchic.physics.particles import PARTICLES

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Calculate efficiency for nucleiQC')
    parser.add_argument('--input', type=str, default='output/analysis_results/AnalysisResults.root', help='Input ROOT file')
    parser.add_argument('--output', type=str, default='output/efficiency/efficiency', help='Output ROOT file')
    parser.add_argument('--pdg', type=int, default=1000020030, help='PDG code of the particle to analyze (default: 1000020030 for He3)')
    args = parser.parse_args()
    
    gStyle.SetOptStat(0)
    
    dataset = Dataset.from_root(args.input, 'O2nucleitablered', 'DF*')
    print(dataset.columns)
    
    read_bit_from_flags =  lambda x, indexbit: (x >> indexbit) & 0b1

    dataset['fFlags_bit0'] = dataset['fFlags'].apply(read_bit_from_flags, args=(0,))
    dataset['fFlags_bit9'] = dataset['fFlags'].apply(read_bit_from_flags, args=(9,))

    dataset.query('fFlags_bit0 == 1', inplace=True) # reconstructed collision
    dataset.query('fFlags_bit9 == 1', inplace=True)  # isPhysicalPrimary
    #dataset.query('fMcProcess == 0')

    print(dataset['fPDGcode'].unique())

    for particle in ['He', 'Pr']:
        
        prepath = '/'.join(args.output.split('/')[:-1])
        output_path =  prepath + '/' + particle + '/' + args.output.split('/')[-1]
        
        pdg = PARTICLES[particle].pdg
        charge = 2 if particle == 'He' else 1
        PT_MAX = 10 if particle == 'He' else 5

        particle_dataset = dataset.query(f'abs(fPDGcode) == {pdg}', inplace=False)
        particle_dataset['fSign'] = particle_dataset['fPDGcode'].apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)

        particle_dataset['fSignedPt'] = particle_dataset['fPt'] * charge #* particle_dataset['fSign']
        particle_dataset['fgSignedPt'] = particle_dataset['fgPt'] #* particle_dataset['fSign']

        h_num = particle_dataset.build_th1('fSignedPt', AxisSpec(40, -PT_MAX, PT_MAX, 'Recontructed', 'Reconstructed;#it{p}_{T} (GeV/c)'))
        set_root_object(h_num, line_color=2) 
        h_den = particle_dataset.build_th1('fgSignedPt', AxisSpec(40, -PT_MAX, PT_MAX, 'Generated', 'Generated;#it{p}_{T} (GeV/c)'))

        h_flag9 = particle_dataset.build_th1('fFlags_bit9', AxisSpec(2, -0.5, 1.5, 'bits'))
        h_dcaxy = particle_dataset.build_th1('fDCAxy', AxisSpec(200, -0.05, 0.05, ';DCA_{xy} (cm);'))
        h_dcaz = particle_dataset.build_th1('fDCAz', AxisSpec(200, -0.05, 0.05, ';DCA_{z} (cm);'))

        h_eff = build_efficiency(h_den, h_num, name='nucleiQC', xtitle='#it{p}_{T} (GeV/c)', ytitle='#varepsilon')

        canvas = TCanvas()
        hframe = canvas.DrawFrame(-PT_MAX, 0, PT_MAX, h_den.GetMaximum() * 1.2, f'nucleiQC;{h_den.GetXaxis().GetTitle()};{h_den.GetYaxis().GetTitle()}')
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
        h_flag9.Write('flag9')
        h_dcaxy.Write('dcaxy')
        h_dcaz.Write('dcaz')
        outfile.Close()
        
        for hist in [h_num, h_den, h_eff, h_flag9, h_dcaxy, h_dcaz]:
            del hist

