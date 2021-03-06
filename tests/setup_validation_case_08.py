# -*- coding: utf-8 -*-
import numpy as np
from base_validation_case import BaseValidationCase
import thermal_building_model.eqAirTemp as eq_air_temp
from common_test_case_parameters import building_data_cases_08_09, equal_air_temperature_parameters_08_09

class SetupValidationCase08(BaseValidationCase):
    def __init__(self, times_per_hour=60, total_days=60):
        super().__init__(times_per_hour, total_days)
    
    def get_building_parameters(self):
        return building_data_cases_08_09
    
    def get_internal_gains_convective(self):
        return self._get_profile(0, 280, 7, 17)
    
    def get_internal_gains_radiative(self):
        return self._get_profile(0, 80, 7, 17)
    
    def get_solar_radiation(self):
        q_sol_rad_win_raw = np.loadtxt("inputs/case08_q_sol_win.csv", usecols=(1,2))
        solarRad_win = q_sol_rad_win_raw[0:24,:]
        solarRad_win[solarRad_win > 100] = solarRad_win[solarRad_win > 100] * 0.15
        solarRad_win_adj = np.repeat(solarRad_win, self.times_per_hour, axis=0)
        
        return np.tile(solarRad_win_adj.T, 60).T

    def get_weather_temperature(self):
        t_outside_raw = np.loadtxt("inputs/case08_t_amb.csv", delimiter=",")
        t_outside = ([t_outside_raw[2*i,1] for i in range(24)])
        t_outside_adj = np.repeat(t_outside, self.times_per_hour)
        
        return np.tile(t_outside_adj, 60)
    
    def get_equal_air_temperature(self):
        solar_radiation = self.get_solar_radiation()
        sunblind_in_tiled = np.zeros_like(solar_radiation)
        sunblind_in_tiled[solar_radiation > 100] = 0.85
        
        t_black_sky = np.zeros(self.total_timesteps) + 273.15
        
        q_sol_rad_wall_raw = np.loadtxt("inputs/case08_q_sol_wall.csv", usecols=(1,2))
        solarRad_wall = q_sol_rad_wall_raw[0:24,:]
        solarRad_wall_adj = np.repeat(solarRad_wall, self.times_per_hour, axis=0)
        solarRad_wall_tiled = np.tile(solarRad_wall_adj.T, 60).T
        
        return eq_air_temp.equal_air_temp(solarRad_wall_tiled, 
                                          t_black_sky, 
                                          self.get_weather_temperature(), 
                                          sunblind_in_tiled, 
                                          equal_air_temperature_parameters_08_09)
    