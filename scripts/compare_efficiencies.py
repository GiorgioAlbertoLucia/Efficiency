
from ROOT import TCanvas, TFile, gStyle


from torchic import Dataset, AxisSpec
from torchic.core.histogram import build_efficiency, load_hist
from torchic.utils.root import set_root_object, init_legend
from torchic.utils.colors import get_color


import argparse

import sys
sys.path.append('../../')
from torchic.physics.particles import PARTICLES

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Calculate efficiency for nucleiQC')
    parser.add_argument('--input', type=str, default='AnalysisResults.root', help='Input ROOT file')
    parser.add_argument('--output', type=str, default='output/efficiency/efficiency', help='Output ROOT file')
    parser.add_argument('--pdg', type=int, default=1000020030, help='PDG code of the particle to analyze (default: 1000020030 for He3)')
    args = parser.parse_args()
    
    gStyle.SetOptStat(0)
    
    outfile = TFile(f'../output/{args.output}', 'RECREATE')
    
    for particle in ['He', 'Pr']:
        
        outdir = outfile.mkdir(particle)
        
        inpath_nucleiQC = f'../nucleiQC/output/efficiency/{particle}/{args.input}'
        inpath_nucleiSpectra = f'../nucleiSpectra/output/efficiency/{particle}/{args.input}'
        
        # pt histograms generated
        h_pt_gen_nucleiQC = load_hist(inpath_nucleiQC, 'denominator')
        set_root_object(h_pt_gen_nucleiQC, line_color=get_color(0), marker_color=get_color(0), name='nucleiQC')
        h_pt_gen_nucleiSpectra = load_hist(inpath_nucleiSpectra, 'denominator')
        set_root_object(h_pt_gen_nucleiSpectra, line_color=get_color(1), marker_color=get_color(1), name='nucleiSpectra')
        
        canvas = TCanvas(f'canvas_pt_gen_{particle}', f'Generated pT Comparison for {particle}', 800, 600)
        hframe = canvas.DrawFrame(h_pt_gen_nucleiQC.GetXaxis().GetXmin(), 0, h_pt_gen_nucleiQC.GetXaxis().GetXmax(), 
                                  max(h_pt_gen_nucleiQC.GetMaximum(), h_pt_gen_nucleiSpectra.GetMaximum())*1.2,
                                  f'{PARTICLES[particle].label};#it{{p}}_{{T}}^{{gen}} (GeV/c);Counts')
        
        legend = init_legend(0.35, 0.6, 0.68, 0.88)
        legend.AddEntry(h_pt_gen_nucleiQC, 'nucleiQC', 'lep')
        legend.AddEntry(h_pt_gen_nucleiSpectra, 'nucleiSpectra', 'lep')
        
        h_pt_gen_nucleiQC.Draw('hist E1 same')
        h_pt_gen_nucleiSpectra.Draw('hist E1 same')
        legend.Draw()
        
        outdir.cd()
        canvas.Write()
        
        # pt histograms reconstructed
        h_pt_rec_nucleiQC = load_hist(inpath_nucleiQC, 'numerator')
        set_root_object(h_pt_rec_nucleiQC, line_color=get_color(0), marker_color=get_color(0), name='nucleiQC')
        h_pt_rec_nucleiSpectra = load_hist(inpath_nucleiSpectra, 'numerator')
        set_root_object(h_pt_rec_nucleiSpectra, line_color=get_color(1), marker_color=get_color(1), name='nucleiSpectra')
        
        canvas = TCanvas(f'canvas_pt_rec_{particle}', f'Reconstructed pT Comparison for {particle}', 800, 600)
        hframe = canvas.DrawFrame(h_pt_rec_nucleiQC.GetXaxis().GetXmin(), 0, h_pt_rec_nucleiQC.GetXaxis().GetXmax(),
                                    max(h_pt_rec_nucleiQC.GetMaximum(), h_pt_rec_nucleiSpectra.GetMaximum())*1.2,
                                    f'{PARTICLES[particle].label};#it{{p}}_{{T}}^{{rec}} (GeV/c);Counts')
        
        legend = init_legend(0.35, 0.6, 0.68, 0.88)
        legend.AddEntry(h_pt_rec_nucleiQC, 'nucleiQC', 'lep')
        legend.AddEntry(h_pt_rec_nucleiSpectra, 'nucleiSpectra', 'lep')
        
        h_pt_rec_nucleiQC.Draw('hist E1 same')
        h_pt_rec_nucleiSpectra.Draw('hist E1 same')
        legend.Draw()
        
        outdir.cd()
        canvas.Write()
        
        # Efficiency histograms
        h_eff_nucleiQC = load_hist(inpath_nucleiQC, 'efficiency')
        set_root_object(h_eff_nucleiQC, line_color=get_color(0), marker_color=get_color(0), name='nucleiQC')
        h_eff_nucleiSpectra = load_hist(inpath_nucleiSpectra, 'efficiency')
        set_root_object(h_eff_nucleiSpectra, line_color=get_color(1), marker_color=get_color(1), name='nucleiSpectra')
        
        canvas = TCanvas(f'canvas_efficiency_{particle}', f'Efficiency Comparison for {particle}', 800, 600)
        hframe = canvas.DrawFrame(h_eff_nucleiQC.GetXaxis().GetXmin(), 0, h_eff_nucleiQC.GetXaxis().GetXmax(), 1.2,
                                  f'{PARTICLES[particle].label};#it{{p}}_{{T}} (GeV/c);Efficiency')
        
        legend = init_legend(0.35, 0.6, 0.68, 0.88)
        legend.AddEntry(h_eff_nucleiQC, 'nucleiQC', 'lep')
        legend.AddEntry(h_eff_nucleiSpectra, 'nucleiSpectra', 'lep')
        
        h_eff_nucleiQC.Draw('hist E1 same')
        h_eff_nucleiSpectra.Draw('hist E1 same')
        legend.Draw()
        
        outdir.cd()
        canvas.Write()
        
    outfile.Close()
        
        
        
        