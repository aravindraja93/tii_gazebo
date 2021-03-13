#!/usr/bin/env python3
"""
Generate Worlds
@author: Benjamin Perseghetti
@email: bperseghetti@rudislabs.com
"""
import jinja2
import argparse
import os
import numpy as np
import datetime

rel_gazebo_path = ".."
rel_world_path ="../worlds"
script_path = os.path.realpath(__file__).replace("jinja_world_gen.py","")
default_env_path = os.path.relpath(os.path.join(script_path, rel_gazebo_path))
default_world_path = os.path.relpath(os.path.join(script_path, rel_world_path))
default_filename = os.path.relpath(os.path.join(default_world_path, "gen.world.jinja"))
default_sdf_world_dict = {
    "empty": 1.5,
    "mcmillan": 1.5,
    "ksql": 1.5,
    "irlock": 1.5,
    "boat": 1.5,
    "baylands": 1.5,
    "yosemite": 1.5,
    "windy": 1.5,
    "warehouse": 1.5,
    "typhoon": 1.5,
    "abu_dhabi": 1.5,
    "raceway": 1.5
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdf_version', default="NotSet", help="SDF format version to use for interpreting world file")
    parser.add_argument('--sun_model', default="sunSolarNoon", help="Select sun model [sunSolarNoon, sunHighShadow, sunUTC, sunNone]")
    parser.add_argument('--sun_utc_date', default="1904_09_20_17_30", help="Date 'YYYY_MM_DD_hh_mm' with UTC time to calculate sunUTC values or 'Now' for your current UTC time.")
    parser.add_argument('--cloud_speed', default="NoClouds", help="Turn on clouds with given speed")
    parser.add_argument('--shadows', default=1, help="Shadows on [1] or off [0]")
    parser.add_argument('--video_widget', default="NotSet", help="GUI video widget on [1] or off [0]")
    parser.add_argument('--update_rate', default=250, help="Real time update rate.")
    parser.add_argument('--wind_speed', default="NotSet", help="Turn on wind with given mean speed.")
    parser.add_argument('--realtime_factor', default=1.0, help="Real time factor.")
    parser.add_argument('--world_name', default="NotSet", help="Name of world, see default_sdf_world_dict for options")
    parser.add_argument('--ambient_light', default=0.5, help="Value for ambient light [0.0..1.0]")
    parser.add_argument('--background_light', default=0.15, help="Value for background light [0.0..1.0]")
    parser.add_argument('--spherical_coords', default="NotSet", help="Enable or disable spherical coordinates on [1] or off [0]")
    parser.add_argument('--latitude', default=39.8039, help="Latitude for spherical coordinates and sunUTC calculation")
    parser.add_argument('--longitude', default=-84.0606, help="Longitude for spherical coordinates and sunUTC calculation")
    parser.add_argument('--altitude', default=244, help="Altitude for spherical coordinates")
    parser.add_argument('--model_name', default="NotSet", help="Model to be used for hitl case in jinja world file")
    parser.add_argument('--model_pose', default="NotSet", help="Pose: 'x y z r p y' of model")
    parser.add_argument('--irlock_beacon_pose', default="NotSet", help="Pose: 'x y z r p y' of irlock beacon")
    parser.add_argument('--ode_threads', default=2, help="Number of island threads to use for ODE.")
    args = parser.parse_args()

    if args.world_name not in default_sdf_world_dict:
        print("\nERROR!!!")
        print('World name: "{:s}" DOES NOT MATCH any entries in default_sdf_world_dict.\nTry world name:'.format(args.world_name))
        for world_option in default_sdf_world_dict:
            print('\t{:s}'.format(world_option))
        print("\nEXITING jinja_world_gen.py...\n")
        exit(1)

    if args.sdf_version == "NotSet":
        args.sdf_version = default_sdf_world_dict.get(args.world_name)
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(default_env_path))
    template = env.get_template(os.path.relpath(default_filename, default_env_path))

    if args.sun_model == "sunUTC":
        try:
            import pysolar
        except ImportError:
            pass
            args.sun_model = "sunNone"

    if args.sun_model == "sunUTC":
        dateStringUTC = args.sun_utc_date
        if dateStringUTC == "Now":
            dateUTC = datetime.datetime.now(datetime.timezone.utc)
        else:
            if len(dateStringUTC) != 16:
                dateStringUTC='1904_09_20_17_30'
            YYYY = int(dateStringUTC[:4])
            MM = int(dateStringUTC[5:7])
            DD = int(dateStringUTC[8:10])
            hh = int(dateStringUTC[11:13])
            mm = int(dateStringUTC[14:16])
            dateUTC = datetime.datetime(YYYY, MM, DD, hh, mm, 0, 0, tzinfo=datetime.timezone.utc)
        sunLatitude = float(args.latitude)
        sunLongitude = float(args.longitude)
        sunAzimuth = pysolar.solar.get_azimuth(sunLatitude, sunLongitude, dateUTC)
        sunAltitude = pysolar.solar.get_altitude(sunLatitude, sunLongitude, dateUTC)
        sunRadiation =  pysolar.radiation.get_radiation_direct(dateUTC, sunAltitude)
        if sunRadiation > 1000.0:
            sunRadiation = 1000.0
        if sunRadiation < 0.0:
            sunRadiation = 0.0
        sunRadiationNorm = sunRadiation/1000.0
        specularRatio = 0.3    
        sunDiffuse = '{:1.3f} {:1.3f} {:1.3f} {:1.3f} 1'.format(sunRadiationNorm,sunRadiationNorm,sunRadiationNorm,sunRadiationNorm)
        sunSpecular = '{:1.3f} {:1.3f} {:1.3f} {:1.3f} 1'.format(specularRatio*sunRadiationNorm,specularRatio*sunRadiationNorm,specularRatio*sunRadiationNorm,specularRatio*sunRadiationNorm)
    
        sunAzimuthRad=sunAzimuth*np.pi/180.0
        sunAltitudeRad=sunAltitude*np.pi/180.0
    
        Xenu = -np.cos(sunAltitudeRad)*np.sin(sunAzimuthRad)
        Yenu = -np.cos(sunAltitudeRad)*np.cos(sunAzimuthRad)
        Zenu = -np.sin(sunAltitudeRad)
    
        sunVector = '{:1.3f} {:1.3f} {:1.3f}'.format(Xenu, Yenu, Zenu)
    
        if sunRadiationNorm == 0:
            args.sun_model="sunNight"
    else:
        sunDiffuse="NotSet"
        sunSpecular="NotSet"
        sunVector="NotSet"

    if args.sun_model == "sunNight":
        print("WARNING: WORLD IS SET TO NIGHT TIME MODE!!!")

    d = {'sdf_version': args.sdf_version, \
         'sun_model': args.sun_model, \
         'sun_diffuse': sunDiffuse, \
         'sun_specular': sunSpecular, \
         'sun_vector': sunVector, \
         'cloud_speed': args.cloud_speed, \
         'shadows': args.shadows, \
         'video_widget': args.video_widget, \
         'wind_speed': args.wind_speed, \
         'update_rate': args.update_rate, \
         'realtime_factor': args.realtime_factor, \
         'ambient_light': args.ambient_light, \
         'background_light': args.background_light, \
         'spherical_coords': args.spherical_coords, \
         'latitude': args.latitude, \
         'altitude': args.altitude, \
         'longitude': args.longitude, \
         'irlock_beacon_pose': args.irlock_beacon_pose, \
         'world_name': args.world_name, \
         'ode_threads': args.ode_threads}

    result = template.render(d)
    filename_out = '/tmp/{:s}.world'.format(args.world_name)

    with open(filename_out, 'w') as f_out:
        print(('{:s} -> {:s}'.format(default_filename, filename_out)))
        f_out.write(result)
