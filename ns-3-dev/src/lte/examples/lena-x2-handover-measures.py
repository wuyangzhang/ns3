# /*
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation;
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  *
#  */

import ns.core
import ns.internet
import ns.mobility
import ns.buildings
import ns.network
import ns.lte
import ns.point_to_point
import ns.applications

def NotifyConnectionEstablishedEnb (imsi, cellid, rnti):
  print "UE IMSI " + str(imsi) + ": connected to CellId " + str(cellid) + " with RNTI " + str(rnti)

def NotifyHandoverJoiningTimeout (rnti):
  print "Handover Joining Timeout for RNTI " + str(rnti)

def NotifyHandoverLeavingTimeout (rnti):
  print "Handover Leaving Timeout for RNTI " + str(rnti)



def main(argv): 

    numUes = 1
    numEnbs = 2
    numBearersPerUe = 0
    distance = 500.0 # m
    yForUe = 500.0   # m
    speed = 20.0       # m/s
    simTime = float(numEnbs + 1) * distance / speed # 1500 m / 20 m/s = 75 secs
    enbTxPowerDbm = 46.0
    
    # Enable logging
    ns.core.LogComponentEnable("A2A4RsrqHandoverAlgorithm", ns.core.LOG_LEVEL_LOGIC)
    
    # change some default attributes so that they are reasonable for
    # this scenario, but do this before processing command line
    # arguments, so that the user is allowed to override these settings
    #ns.core.Config.SetDefault ("ns3::UdpClient::Interval", ns.core.TimeValue (ns.core.MilliSeconds (10)))
    #ns.core.Config.SetDefault ("ns3::UdpClient::MaxPackets", ns.core.UintegerValue (1000000))
    ns.core.Config.SetDefault ("ns3::LteHelper::UseIdealRrc", ns.core.BooleanValue (1))
    
    # Command line arguments
    #cmd = ns.core.CommandLine()
    #cmd.AddValue ("simTime", "Total duration of the simulation (in seconds)", simTime)
    #cmd.AddValue ("speed", "Speed of the UE (default = 20 m/s)", speed);
    #cmd.AddValue ("enbTxPowerDbm", "TX power [dBm] used by HeNBs (default = 46.0)", enbTxPowerDbm)
    #cmd.Parse(argv)
    
    lteHelper = ns.lte.LteHelper()
    epcHelper = ns.lte.PointToPointEpcHelper()
    lteHelper.SetEpcHelper(epcHelper)

    lteHelper.SetSchedulerType ("ns3::RrFfMacScheduler");
    
    lteHelper.SetHandoverAlgorithmType ("ns3::A2A4RsrqHandoverAlgorithm");
    lteHelper.SetHandoverAlgorithmAttribute ("ServingCellThreshold",
                                              ns.core.UintegerValue (30));
    lteHelper.SetHandoverAlgorithmAttribute ("NeighbourCellOffset",
                                              ns.core.UintegerValue (1));
                                              
    pgw = epcHelper.GetPgwNode()
    
    # Create a single RemoteHost
    remoteHostContainer = ns.network.NodeContainer()
    remoteHostContainer.Create(1)
    remoteHost = remoteHostContainer.Get(0)

    internet = ns.internet.InternetStackHelper()
    internet.Install (remoteHostContainer)
    
    # Create the Internet
    p2ph = ns.point_to_point.PointToPointHelper()
    p2ph.SetDeviceAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate ("100Gb/s")))
    p2ph.SetDeviceAttribute ("Mtu", ns.core.UintegerValue (1500))
    p2ph.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.Seconds (0.010)))
    internetDevices = p2ph.Install (pgw, remoteHost)
    ipv4h = ns.internet.Ipv4AddressHelper()
    ipv4h.SetBase (ns.network.Ipv4Address("1.0.0.0"), ns.network.Ipv4Mask("255.0.0.0"))
    internetIpIfaces = ipv4h.Assign (internetDevices)
    remoteHostAddr = internetIpIfaces.GetAddress (1)

    # Routing of the Internet Host (towards the LTE network)
    ipv4RoutingHelper = ns.internet.Ipv4StaticRoutingHelper()
    remoteHostStaticRouting = ipv4RoutingHelper.GetStaticRouting (remoteHost.GetObject (ns.internet.Ipv4.GetTypeId()))
    # interface 0 is localhost, 1 is the p2p device
    remoteHostStaticRouting.AddNetworkRouteTo (ns.network.Ipv4Address ("7.0.0.0"), ns.network.Ipv4Mask ("255.0.0.0"), 1)
  
#    * Network topology:
#    *
#    *      |     + --------------------------------------------------------->
#    *      |     UE
#    *      |
#    *      |               d                   d                   d
#    *    y |     |-------------------x-------------------x-------------------
#    *      |     |                 eNodeB              eNodeB
#    *      |   d |
#    *      |     |
#    *      |     |                                             d = distance
#    *            o (0, 0, 0)                                   y = yForUe
   
    enbNodes = ns.network.NodeContainer()
    ueNodes = ns.network.NodeContainer()
    enbNodes.Create(numEnbs)
    ueNodes.Create(numUes)
    
    # Install Mobility Model in eNB
    enbPositionAlloc = ns.mobility.ListPositionAllocator()
    for i in range(0, numEnbs):
        enbPosition = ns.core.Vector(distance * (i + 1), distance, 0)
        enbPositionAlloc.Add(enbPosition)

    enbMobility = ns.mobility.MobilityHelper()
    enbMobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    enbMobility.SetPositionAllocator (enbPositionAlloc)
    enbMobility.Install(enbNodes)
    
    # Install Mobility Model in UE
    ueMobility = ns.mobility.MobilityHelper()
    ueMobility.SetMobilityModel("ns3::ConstantVelocityMobilityModel")
    ueMobility.Install(ueNodes)
    ueNodes.Get (0).GetObject (ns.mobility.MobilityModel.GetTypeId()).SetPosition (ns.core.Vector (0, yForUe, 0))
    ueNodes.Get (0).GetObject (ns.mobility.ConstantVelocityMobilityModel.GetTypeId()).SetVelocity (ns.core.Vector (speed, 0, 0))

    # Install LTE Devices in eNB and UEs
    ns.core.Config.SetDefault ("ns3::LteEnbPhy::TxPower", ns.core.DoubleValue (enbTxPowerDbm))
    enbLteDevs = lteHelper.InstallEnbDevice(enbNodes)
    ueLteDevs = lteHelper.InstallUeDevice(ueNodes)
    
    # Install the IP stack on the UEs
    internet.Install(ueNodes)
    ueIpIfaces = epcHelper.AssignUeIpv4Address (ueLteDevs)

    # Attach all UEs to the first eNodeB
    for i in range(0, numUes):
        lteHelper.Attach(ueLteDevs.Get (i), enbLteDevs.Get(0))
    
    # NS_LOG_LOGIC ("setting up applications");
    # Install and start applications on UEs and remote host
    dlPort = 10000
    ulPort = 20000
    
    # randomize a bit start times to avoid simulation artifacts
    # (e.g., buffer overflows due to packet transmissions happening
    # exactly at the same time)
    startTimeSeconds = ns.core.UniformRandomVariable ()
    startTimeSeconds.SetAttribute ("Min", ns.core.DoubleValue (0))
    startTimeSeconds.SetAttribute ("Max", ns.core.DoubleValue (0.010))
    
    for u in range(0, numUes):
         ue = ueNodes.Get (u)
         ueTmpContainer = ns.network.NodeContainer()
         ueTmpContainer.Add(ue)
         # Set the default gateway for the UE
         ueStaticRouting = ipv4RoutingHelper.GetStaticRouting (ue.GetObject (ns.internet.Ipv4.GetTypeId()))
         ueStaticRouting.SetDefaultRoute (epcHelper.GetUeDefaultGatewayAddress (), 1)
         for b in range(0, numBearersPerUe):
             dlPort += 1
             ulPort += 1
             clientApps = ns.network.ApplicationContainer()
             serverApps = ns.network.ApplicationContainer()

             # NS_LOG_LOGIC ("installing UDP DL app for UE " << u);
             dlClientHelper = ns.applications.UdpClientHelper(ueIpIfaces.GetAddress (u), dlPort)
             clientApps.Add (dlClientHelper.Install (remoteHostContainer))
             dlPacketSinkHelper = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", \
                                                                   ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), dlPort))
             serverApps.Add (dlPacketSinkHelper.Install (ueTmpContainer))

             # NS_LOG_LOGIC ("installing UDP UL app for UE " << u);
#              ulClientHelper = ns.applications.UdpClientHelper(remoteHostAddr, ulPort)
#              clientApps.Add (ulClientHelper.Install (ueTmpContainer))
#              ulPacketSinkHelper = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", \
#                                                                    ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), ulPort))
#              serverApps.Add (ulPacketSinkHelper.Install (remoteHostContainer))

             tft = ns.lte.EpcTft ()
             dlpf = ns.lte.EpcTft.PacketFilter()
             dlpf.localPortStart = dlPort
             dlpf.localPortEnd = dlPort
             tft.Add (dlpf)
             ulpf = ns.lte.EpcTft.PacketFilter()
             ulpf.remotePortStart = ulPort
             ulpf.remotePortEnd = ulPort
             tft.Add (ulpf)
             bearer = ns.lte.EpsBearer(ns.lte.EpsBearer.NGBR_VIDEO_TCP_DEFAULT)
             lteHelper.ActivateDedicatedEpsBearer (ueLteDevs.Get (u), bearer, tft)

             startTime = ns.core.Seconds (startTimeSeconds.GetValue ())
             serverApps.Start (startTime)
             clientApps.Start (startTime)

    
    # Add X2 interface
    lteHelper.AddX2Interface (enbNodes)
    
    lteHelper.EnablePhyTraces ()
    lteHelper.EnableMacTraces ()
    lteHelper.EnableRlcTraces ()
    lteHelper.EnablePdcpTraces ()
    
    rlcStats = lteHelper.GetRlcStats ()
    rlcStats.SetAttribute ("EpochDuration", ns.core.TimeValue (ns.core.Seconds (1.0)));
    pdcpStats = lteHelper.GetPdcpStats ();
    pdcpStats.SetAttribute ("EpochDuration", ns.core.TimeValue (ns.core.Seconds (1.0)));
    
    # Set RRC callbacks
#     ns.core.Config.Connect ("/NodeList/*/DeviceList/*/LteUeRrc/ConnectionEstablished", \
#                             NotifyConnectionEstablishedUe)
    enbLteDevs.Get(0).GetRrc().SetConnectionEstablishedCallback(NotifyConnectionEstablishedEnb)
    enbLteDevs.Get(0).GetRrc().SetHandoverJoiningTimeoutCallback(NotifyHandoverJoiningTimeout)
    enbLteDevs.Get(0).GetRrc().SetHandoverLeavingTimeoutCallback(NotifyHandoverLeavingTimeout)
        
    print ("Run Simulation.")
    ns.core.Simulator.Stop(ns.core.Seconds(simTime))
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()


if __name__ == '__main__':
    import sys
    main(sys.argv)


