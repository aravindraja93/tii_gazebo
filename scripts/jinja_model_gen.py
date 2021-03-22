#!/usr/bin/env python3
"""
Generate Models
@author: Benjamin Perseghetti
@email: bperseghetti@rudislabs.com
"""
import jinja2
import argparse
import os
import numpy as np

rel_gazebo_path = ".."
rel_model_path ="../models"
script_path = os.path.realpath(__file__).replace("jinja_model_gen.py","")
default_env_path = os.path.relpath(os.path.join(script_path, rel_gazebo_path))
default_model_path = os.path.relpath(os.path.join(script_path, rel_model_path))
default_sdf_dict = {
    "iris": 1.6,
    "plane": 1.5,
    "standard_vtol": 1.5
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_model', default="NotSet", help="Base model jinja file EX: iris")
    parser.add_argument('--sdf_version', default="NotSet", help="SDF format version to use for interpreting model file")
    parser.add_argument('--mavlink_tcp_port', default=4560, help="TCP port for PX4 SITL")
    parser.add_argument('--mavlink_udp_port', default=14560, help="Mavlink UDP port for mavlink access")
    parser.add_argument('--qgc_udp_port', default=14550, help="QGC UDP port")
    parser.add_argument('--sdk_udp_port', default=14540, help="SDK UDP port")
    parser.add_argument('--serial_enabled', default="NotSet", help="Enable serial device for HITL")
    parser.add_argument('--serial_device', default="/dev/ttyACM0", help="Serial device for FMU")
    parser.add_argument('--serial_baudrate', default=921600, help="Baudrate of Serial device for FMU")
    parser.add_argument('--enable_lockstep', default="NotSet", help="Enable lockstep for simulation")
    parser.add_argument('--gps_attack_time', default="NotSet", help="GPS attack time sec")
    parser.add_argument('--gps_attack_rate', default="NotSet", help="GPS attack rate m/s")
    parser.add_argument('--gps_model_name', default="NotSet", help="GPS model name")
    parser.add_argument('--hil_mode', default=0, help="Enable HIL mode for HITL simulation")
    parser.add_argument('--model_name', default="NotSet", help="Model to be used in jinja files")
    args = parser.parse_args()

    if args.base_model not in default_sdf_dict:
        print("\nWARNING!!!")
        print('Base model: "{:s}" DOES NOT MATCH any entries in default_sdf_dict.\nTry base model name:'.format(args.base_model))
        for model_option in default_sdf_dict:
            print('\t{:s}'.format(model_option))
        print("\nEXITING jinja_model_gen.py...\n")
        exit(1)

    if args.model_name == "NotSet":
        args.model_name = args.base_model
    
    if args.sdf_version == "NotSet":
        args.sdf_version = default_sdf_dict.get(args.base_model)
        
    input_filename = os.path.relpath(os.path.join(default_model_path, '{:s}/{:s}.sdf.jinja'.format(args.base_model,args.base_model)))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(default_env_path))
    template_model = env.get_template(os.path.relpath(input_filename, default_env_path))
    
    if args.serial_enabled=="NotSet":
        args.serial_enabled=0

    if args.enable_lockstep=="NotSet":
        args.enable_lockstep=1

    d = {'sdf_version': args.sdf_version, \
         'mavlink_tcp_port': args.mavlink_tcp_port, \
         'mavlink_udp_port': args.mavlink_udp_port, \
         'qgc_udp_port': args.qgc_udp_port, \
         'sdk_udp_port': args.sdk_udp_port, \
         'serial_enabled': args.serial_enabled, \
         'serial_device': args.serial_device, \
         'serial_baudrate': args.serial_baudrate, \
         'enable_lockstep': args.enable_lockstep, \
         'gps_attack_time': args.gps_attack_time, \
         'gps_attack_rate': args.gps_attack_rate, \
         'gps_model_name': args.gps_model_name, \
         'model_name': args.model_name, \
         'hil_mode': args.hil_mode}

    model_result = template_model.render(d)
    model_out = '/tmp/{:s}.sdf'.format(args.model_name)
        
    with open(model_out, 'w') as m_out:
        print(('{:s} -> {:s}'.format(input_filename, model_out)))
        m_out.write(model_result)

    if args.gps_model_name != "NotSet" and args.gps_model_name != "gps":
        
        if (not os.path.isdir('/tmp/models/gps')):
            try: 
                os.makedirs('/tmp/models/gps', exist_ok = True) 
            except OSError as error: 
                print("Directory creation error.")

        input_gps = os.path.relpath(os.path.join(default_model_path, 'gps/gps.sdf.jinja'))
        template_gps = env.get_template(os.path.relpath(input_gps, default_env_path))
        gps_result = template_gps.render(d)
        gps_out = '/tmp/models/gps/{:s}.sdf'.format(args.gps_model_name)
        with open(gps_out, 'w') as g_out:
            print(('{:s} -> {:s}'.format("gps/gps.sdf.jinja", gps_out)))
            g_out.write(gps_result)
        
        input_gps_config = os.path.relpath(os.path.join(default_model_path, 'gps/model.config.jinja'))
        template_gps_config = env.get_template(os.path.relpath(input_gps_config, default_env_path))
        gps_result_config = template_gps_config.render(d)
        gps_out_config = '/tmp/models/gps/model.config'
        with open(gps_out_config, 'w') as gc_out:
            print(('{:s} -> {:s}'.format("gps/model.config.jinja", gps_out_config)))
            gc_out.write(gps_result_config)
