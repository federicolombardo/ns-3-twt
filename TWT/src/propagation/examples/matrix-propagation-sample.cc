#include <cmath>
#include <limits>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

// ------- Utility functions for conversion: SNR(dB) -> PathLoss(dB) -----------------
static double NoiseDbm(double bandwidthHz, double noiseFigureDb)
{
  // Thermal noise power at room temperature: -174 dBm/Hz
  // 10.0 * std::log10(bandwidthHz) -> converts noise from dBm/Hz to Hz over bandwidth
  // noiseFigureDb adds the receiver noise figure, modeling extra noise introduced by the hardware
  return -174.0 + 10.0 * std::log10(bandwidthHz) + noiseFigureDb; // dBm
}

static double PathLossFromSnr(double snrDb,
                 double txDbm, double gtDb, double grDb,
                 double bandwidthHz, double noiseFigureDb)
{
  const double nDbm = NoiseDbm(bandwidthHz, noiseFigureDb);  // Get the noise power (see function above)
  const double rxDbm = snrDb + nDbm; // Compute the RSSI from SNR and noise power
  return txDbm + gtDb + grDb - rxDbm; // Compute path loss including the TX antenna gain (gtDb) and RX antenna gain (grDb)
}

static void UpdateSnr(Ptr<MatrixPropagationLossModel> matrix,
           Ptr<MobilityModel> txMob,
           Ptr<MobilityModel> rxMob,
           double snrDb,
           double txPowerDbm,
           double bandwidthHz,
           double noiseFigDb)
{
  // Force an SNR value by computing the corresponding path loss
  const double lossDb = PathLossFromSnr(snrDb, txPowerDbm, 0.0, 0.0, bandwidthHz, noiseFigDb);
  matrix->SetLoss(txMob, rxMob, lossDb, true /*symmetric*/);
}

// cache of last RSSI/Noise observed at RX PHY
static double g_lastRssiDbm  = std::numeric_limits<double>::quiet_NaN();
static double g_lastNoiseDbm = std::numeric_limits<double>::quiet_NaN();

static void OnMonitorSnifferRx(Ptr<const Packet> /*p*/,
                    uint16_t /*channelFreqMhz*/,
                    WifiTxVector /*txVector*/,
                    MpduInfo /*aMpdu*/,
                    SignalNoiseDbm signalNoise,
                    uint16_t /*extra*/)
{
  g_lastRssiDbm  = signalNoise.signal;
  g_lastNoiseDbm = signalNoise.noise;
}

// Rx application trace (PacketSink::Rx)
static void OnPacketRx(Ptr<const Packet>, const Address&)
{
  if (std::isnan(g_lastRssiDbm))
    {
      NS_LOG_UNCOND("Packet received at " << Simulator::Now().GetSeconds()
                                           << "s (RSSI not yet known)");
    }
  else
    {
      NS_LOG_UNCOND("Packet received at " << Simulator::Now().GetSeconds()
                                           << "s, RSSI = " << g_lastRssiDbm
                                           << " dBm, Noise = " << g_lastNoiseDbm << " dBm");
    }
}

// ------- Main ----------------------------------------------
int main(int argc, char *argv[])
{
  // Wi-Fi PHY parameters
  double txPowerDbm   = 30.0; // WifiPhy Tx power
  double rxNoiseFigDb = 7.0; // WifiPhy RxNoiseFigure - Typical Wi-Fi RF frontends have noise figures on the order of 5–10 dB - default value in ns-3 PHY: 7 dB
  double bandwidthHz  = 20e6; // Wi-Fi channel width in Hz

  // Create nodes and mobility (mobility can be static as distance does not matter anymore, since we force the SNR)
  NodeContainer nodes; nodes.Create(2);
  MobilityHelper mobility;
  mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
  mobility.Install(nodes);

  // Using MatrixPropagationLossModel so we can force SNR (otherwise, forcing the SNR by editing the PHY and MAC models can be quite challenging)
  Ptr<YansWifiChannel> channel = CreateObject<YansWifiChannel>();
  Ptr<MatrixPropagationLossModel> matrix = CreateObject<MatrixPropagationLossModel>();
  channel->SetPropagationLossModel(matrix);
  channel->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());

  // PHY and MAC configuration
  YansWifiPhyHelper phy;
  phy.SetChannel(channel);
  phy.Set("TxPowerStart", DoubleValue(txPowerDbm));
  phy.Set("TxPowerEnd",   DoubleValue(txPowerDbm));
  phy.Set("RxNoiseFigure", DoubleValue(rxNoiseFigDb));

  WifiHelper wifi;
  wifi.SetStandard(WIFI_STANDARD_80211ax_6GHZ); // Using 802.11ax
  wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                "DataMode", StringValue("HtMcs7"),
                                "ControlMode", StringValue("HtMcs0"));

  // This example considers an ad-hoc network for simplicity
  WifiMacHelper mac;
  mac.SetType("ns3::AdhocWifiMac");

  NetDeviceContainer devices = wifi.Install(phy, mac, nodes);

  // Connect PHY RSSI/Noise trace only on the receiver PHY (node 1), so that we can print the RSSI and noise power for each received packet
  {
    Ptr<WifiNetDevice> rxWifiDev = DynamicCast<WifiNetDevice>(devices.Get(1));
    Ptr<WifiPhy> rxPhy = rxWifiDev->GetPhy();
    rxPhy->TraceConnectWithoutContext("MonitorSnifferRx",
                                       MakeCallback(&OnMonitorSnifferRx));
  }

  // Confugure Internet + IPv4 stack
  InternetStackHelper stack; stack.Install(nodes);
  Ipv4AddressHelper address; address.SetBase("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer ifs = address.Assign(devices);

  // Receiver configuration - receiving UDP packets
  uint16_t port = 4000;
  PacketSinkHelper sink("ns3::UdpSocketFactory",
                         InetSocketAddress(Ipv4Address::GetAny(), port));
  ApplicationContainer sinkApps = sink.Install(nodes.Get(1));
  sinkApps.Start(Seconds(0.0));
  sinkApps.Stop(Seconds(10.0));
  sinkApps.Get(0)->TraceConnectWithoutContext("Rx", MakeCallback(&OnPacketRx));

  // Transmitter configuration - sending UDP packets (1 per second)
  UdpClientHelper client(ifs.GetAddress(1), port);
  client.SetAttribute("MaxPackets", UintegerValue(100));
  client.SetAttribute("Interval",   TimeValue(Seconds(1.0)));
  client.SetAttribute("PacketSize", UintegerValue(200));
  ApplicationContainer clientApp = client.Install(nodes.Get(0));
  clientApp.Start(Seconds(1.0));
  clientApp.Stop(Seconds(10.0));

  // In this simple example, we force the SNR to start from 0, and be increased every second of 10 dB
  Ptr<MobilityModel> txMob = nodes.Get(0)->GetObject<MobilityModel>();
  Ptr<MobilityModel> rxMob = nodes.Get(1)->GetObject<MobilityModel>();

  for (int i = 0; i < 10; ++i)
    {
      double snr = i * 10.0;
      Simulator::Schedule(Seconds(i), [=]() {
        UpdateSnr(matrix, txMob, rxMob, snr, txPowerDbm, bandwidthHz, rxNoiseFigDb);
      });
    }

  // We run then a simple 10 seconds simulation
  Simulator::Stop(Seconds(10.0));
  Simulator::Run();
  Simulator::Destroy();

  return 0;
}
