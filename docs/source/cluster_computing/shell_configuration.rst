2.2.	Shell Configuration
-------------------------
Freesurfer and FSL are automatically configured in the bash and c-shell terminals on the master and core nodes using the fsl.sh (bash) and fsl.csh (c-shell) configuration files in the /etc/profile.d directory. These files also contain additional setup variables for the cluster including the configuration of SUBJECTS_DIR and local mounts of AWS S3 directories. These variables are defined in Table 8.
