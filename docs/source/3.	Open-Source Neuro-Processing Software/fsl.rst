3.3.	FSL
FMRIB Software Library (FSL) is a library of fMRI, MRI and DTI analysis tools developed by Oxford University, UK. The current installed version is 6.0.4.
3.3.1.	Location
The fsl package is located at /usr/share/fsl/6.0. This path is stored in the FSL_DIR variable available in bash and c-shell terminals.
3.3.2.	Common Functions
i.	fsl
Main GUI for FSL. This GUI can be used to create individual and higher-level designs for fMRI analyses, execute individual or higher-level designs of fMRI analyses, run brain extraction, process DTI, perform registration, perform ICA for resting-state fMRI, or generate simulated MRI scans. Details can be found at:
https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSL. 
The specific version installed on this system at:
http://neuro.debian.net/pkgs/fsl-complete.html. 
ii.	fsleyes
MRI visualization GUI. The user guide can be found at:
https://users.fmrib.ox.ac.uk/~paulmc/fsleyes/userdoc/latest/. 
iii.	feat
Command line tool to execute fMRI design files. More info can be found at:
https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FEAT. 
iv.	randomise and randomise_parallel
Randomise is a non-parametric permutation inference tool for neuroimaging data. Randomise utilizes modelling and inferences using standard designs as used in FEAT. The main pitfall of randomize is the accommodation of correlated datasets (repeated measures). However, some cases of repeated measures can be accommodated.
v.	oxford_asl and BASIL
Oxford_asl is a command line utility that can quantify cerebral perfusion (CBF) data from ASL, including motion-correction, registration, partial volume correction, and distortion correction. Command line user guide is available at:
https://asl-docs.readthedocs.io/en/latest/oxford_asl_userguide.html. 
BASIL is the GUI-based version of oxford_asl. Documentation on BASIL is available at:
https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BASIL. 
