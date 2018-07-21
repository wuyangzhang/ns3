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

def main(argv): 

    numEnb = 1
    numUe = 1
    stopTime = 1.05
    
    cmd = ns.core.CommandLine()
    cmd.Parse(argv)
    
    lteHelper = ns.lte.LteHelper()

    enbNodes = ns.network.NodeContainer()
    ueNodes = ns.network.NodeContainer()
    enbNodes.Create(numEnb)
    ueNodes.Create(numUe)

    mobility = ns.mobility.MobilityHelper()
    buildings = ns.buildings.BuildingsHelper()
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(enbNodes)
    buildings.Install(enbNodes)
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
    mobility.Install(ueNodes)
    buildings.Install(ueNodes)
    
    enbDevs = lteHelper.InstallEnbDevice(enbNodes)
    ueDevs = lteHelper.InstallUeDevice(enbNodes)
    lteHelper.Attach(ueDevs, enbDevs.Get(0))

    qci = ns.lte.EpsBearer.GBR_CONV_VOICE
    bearer = ns.lte.EpsBearer(qci)
    lteHelper.ActivateDataRadioBearer(ueDevs, bearer)
    lteHelper.EnableTraces()
    

    print ("Run Simulation.")
    ns.core.Simulator.Stop(ns.core.Seconds(stopTime))
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()


if __name__ == '__main__':
    import sys
    main(sys.argv)


