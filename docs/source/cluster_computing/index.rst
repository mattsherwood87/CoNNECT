:topic: NPC

******************************
Neuro-Processing Cluster (NPC)
******************************

The CoNNECT NPC is a collection of systems that are centrally and locally managed. The resources are all centrally located and under
the control of Wright State Computing and Telecommunications (CaTS). The CoNNECT NPC operates on a network isolated from the main WSU
campus network.

**Jumpbox**

The jumpbox is a user-specific virtual machine (VM) running either windows or linux. The jumpbox is NIST and HIPPA compliant. A user accesses 
their jumpbox VM via VMware Horizon when connected to WSU's secure network or LAN, or connected to the network via virtual private network 
(VPN). Users can access the remainder of the CoNNECT NPC via their jumpbox.

**Master Node**

The master node is the main controller of the CoNNECT NPC. Users access the master node via secure shell (SSH) connections through their 
jumpbox. The master node has 40 physical cores and 756GB RAM, and is running Ubuntu 20.04. 


**Core Node(s)**

Core nodes are the workhorse of the CoNNECT NPC. The core nodes run the same operating system as the master, Ubuntu 20.04. Currently, there 
is a single core node with 40 physical cores and 756GB RAM. Processing can be conducted utilizing the core node(s) by supplying the *submit*
option to the programs described within this manual


.. include:: open-source_software.rst

.. include:: MySQL_database.rst
