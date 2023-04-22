

CoNNECT Systems Overview
########################

The CoNNECT MRI facility consists of several components described below.

Philips 3.0T Ingenia Cx
***********************

The CoNNECT MRI facility was created when Dr. Sherwood received funding from the Air Force Office of Scientific Research and State of Ohio
Department of Higher Education to purchase and install a 3-Tesla (T) MRI for the enhancement of defense-related research. The MRI scanner 
installation was completed on March 31, 2022. The Philips 3.0T Ingenia Cx is obviously at the core of the CoNNECT. This MRI is capable of 
performing state-of-the-art functional and anatomical neuroimaging. Additional MRI components can be found at the `equipment section of 
the CoNNECT website<https://science-math.wright.edu/lab/center-of-neuroimaging-and-neuro-evaluation-of-cognitive-technologies/equipment>`_.

.. include:: data_storage.rst

CoNNECT Neuro-Processing Cluster (NPC)
**************************************

The CoNNECT NPC is a collection of systems that are centrally and locally managed. The resources are all centrally located and under
the control of Wright State Computing and Telecommunications (CaTS). The CoNNECT NPC operates on a network isolated from the main WSU
campus network.

**:doc:`Jumpbox<../cluster_computing/jumpbox.rst>`**

The jumpbox is a user-specific virtual machine (VM) running either windows or linux. The jumpbox is NIST and HIPPA compliant. A user accesses 
their jumpbox VM via VMware Horizon when connected to WSU's secure network or LAN, or connected to the network via virtual private network 
(VPN). Users can access the remainder of the CoNNECT NPC via their jumpbox.

**:doc:`Master Node<../cluster_computing/master.rst>`**

The master node is the main controller of the CoNNECT NPC. Users access the master node via secure shell (SSH) connections through their 
jumpbox. The master node has 40 physical cores and 756GB RAM, and is running Ubuntu 20.04. 

**:doc:`Core Node(s)<../cluster_computing/cores.rst>`**

Core nodes are the workhorse of the CoNNECT NPC. The core nodes run the same operating system as the master, Ubuntu 20.04. Currently, there 
is a single core node with 40 physical cores and 756GB RAM. Processing can be conducted utilizing the core node(s) by supplying the *submit*
option to the programs described within this manual
