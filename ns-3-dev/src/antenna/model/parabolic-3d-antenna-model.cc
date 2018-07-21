/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2012 CTTC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author: Russell Ford <russell.ford@samsung.com>
 */


#include <ns3/log.h>
#include <ns3/double.h>
#include <cmath>

#include "antenna-model.h"
#include "parabolic-3d-antenna-model.h"


namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("Parabolic3DAntennaModel");

NS_OBJECT_ENSURE_REGISTERED (Parabolic3DAntennaModel);


TypeId 
Parabolic3DAntennaModel::GetTypeId ()
{
  static TypeId tid = TypeId ("ns3::Parabolic3DAntennaModel")
    .SetParent<AntennaModel> ()
    .SetGroupName("Antenna")
    .AddConstructor<Parabolic3DAntennaModel> ()
    .AddAttribute ("Beamwidth",
                   "The 3dB horizontal/azimuthal beamwidth (degrees)",
                   DoubleValue (70),
                   MakeDoubleAccessor (&Parabolic3DAntennaModel::SetBeamwidthHoriz,
                                       &Parabolic3DAntennaModel::GetBeamwidthHoriz),
                   MakeDoubleChecker<double> (0, 180))
		.AddAttribute ("BeamwidthVert",
									 "The 3dB vertical/elevational beamwidth (degrees)",
									 DoubleValue (10),
									 MakeDoubleAccessor (&Parabolic3DAntennaModel::SetBeamwidthVert,
																			 &Parabolic3DAntennaModel::GetBeamwidthVert),
									 MakeDoubleChecker<double> (0, 180))
    .AddAttribute ("Orientation",
                   "The angle (degrees) that expresses the OrientationHoriz of the antenna on the x-y-z plane relative to the x axis",
                   DoubleValue (0.0),
                   MakeDoubleAccessor (&Parabolic3DAntennaModel::SetOrientation,
                                       &Parabolic3DAntennaModel::GetOrientation),
                   MakeDoubleChecker<double> (-360, 360))
		.AddAttribute ("Downtilt",
									 "The angle (degrees) that expresses the OrientationHoriz of the antenna on the x-y-z plane relative to the z axis",
									 DoubleValue (9.0),
									 MakeDoubleAccessor (&Parabolic3DAntennaModel::SetDowntilt,
																			 &Parabolic3DAntennaModel::GetDowntilt),
									 MakeDoubleChecker<double> (-360, 360))
    .AddAttribute ("MaxAttenuation",
                   "The maximum attenuation (dB) of the antenna radiation pattern in the horizonal (azimuth) plane.",
                   DoubleValue (25.0),
                   MakeDoubleAccessor (&Parabolic3DAntennaModel::m_maxAttenuationHoriz),
                   MakeDoubleChecker<double> ())
		.AddAttribute ("MaxAttenuationVert",
									 "The maximum attenuation (dB) of the antenna radiation pattern in the vertical (elevation) plane.",
									 DoubleValue (20.0),
									 MakeDoubleAccessor (&Parabolic3DAntennaModel::m_maxAttenuationVert),
									 MakeDoubleChecker<double> ())
		.AddAttribute ("Gain",
									 "The reference antenna gain",
									 DoubleValue (0.0),
									 MakeDoubleAccessor (&Parabolic3DAntennaModel::m_gain),
									 MakeDoubleChecker<double> ())
  ;
  return tid;
}

void 
Parabolic3DAntennaModel::SetBeamwidthHoriz (double beamwidthDegrees)
{ 
  NS_LOG_FUNCTION (this << beamwidthDegrees);
  m_beamwidthHoriz = beamwidthDegrees;
}

double
Parabolic3DAntennaModel::GetBeamwidthHoriz () const
{
  return m_beamwidthHoriz;
}

void 
Parabolic3DAntennaModel::SetBeamwidthVert (double beamwidthDegrees)
{
  NS_LOG_FUNCTION (this << beamwidthDegrees);
  m_beamwidthVert = beamwidthDegrees;
}

double
Parabolic3DAntennaModel::GetBeamwidthVert () const
{
	return m_beamwidthVert;
}


void
Parabolic3DAntennaModel::SetOrientation (double orientationDegrees)
{
  NS_LOG_FUNCTION (this << orientationDegrees);
  m_orientationHoriz = orientationDegrees;
}

double
Parabolic3DAntennaModel::GetOrientation () const
{
	return m_orientationHoriz;
}

void
Parabolic3DAntennaModel::SetDowntilt (double downtilt)
{
  NS_LOG_FUNCTION (this << downtilt);
  m_downtilt = downtilt;
}

double
Parabolic3DAntennaModel::GetDowntilt () const
{
	return m_downtilt;
}

void
Parabolic3DAntennaModel::SetAntennaGain (double gainDb)
{
  NS_LOG_FUNCTION (this << gainDb);
  m_gain = gainDb;
}

double
Parabolic3DAntennaModel::GetAntennaGain() const
{
	return m_gain;
}

double 
Parabolic3DAntennaModel::GetGainDb (Angles a)
{
  NS_LOG_FUNCTION (this << a);
  // azimuth angle w.r.t. the reference system of the antenna
  double phi = std::abs(RadiansToDegrees(a.phi) - m_orientationHoriz);

  //   make sure phi is in (-180, 180]
	while (phi <= -180)
		{
			phi += 360;
		}
	while (phi > 180)
		{
			phi -= 360;
		}

  NS_LOG_LOGIC ("phi = " << phi );

  double gainHoriz = std::max (-12 * pow (phi / m_beamwidthHoriz, 2), -m_maxAttenuationHoriz);

  double theta = RadiansToDegrees(a.theta) - m_downtilt;

  //   make sure theta is in (-180, 180]
	while (theta <= -180)
		{
			theta += 360;
		}
	while (theta > 180)
		{
			theta -= 360;
		}

  double gainVert = std::max (-12 * pow (theta / m_beamwidthVert, 2), -m_maxAttenuationVert);

  double gainDb = std::max(gainHoriz + gainVert, -m_maxAttenuationHoriz) + m_gain;

  NS_LOG_LOGIC ("gain = " << gainDb);
  return gainDb;
}


}

