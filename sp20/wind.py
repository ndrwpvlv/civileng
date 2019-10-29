# -*- coding: utf-8 -*-


from numpy import array, copy


class WindSP20:

    def __init__(self, zone: str, zone_type: str, d_width: float,
                 h_height: float, building_type: int = 2):
        """
        zone - ветровой район ('1a', '1', ...)
        zone_type - тип местности ('A', 'B', 'C')
        d_width - ширина здания поперек ветрового потока
        h_height - высота здания
        building_type - тип здания: 1 - башня, труба и т.п., 2 - обычное здание
        """
        self.zone = zone
        self.zone_type = zone_type
        self.w_0 = self.calc_w_0(self.zone)
        self.d = abs(d_width)
        self.h = abs(h_height)
        self.building_type = building_type
        self.z_e = self.calc_z_e()
        self.k_ze = self.calc_k_ze(self.zone_type, self.z_e)

    @staticmethod
    def calc_w_0(zone: str):
        """
        Определение нормативного значения ветрового давление

        Параметры:
            self.zone - ветровой район (тип str)
        """
        tab_11_1 = {'1a': 0.17, '1': 0.23, '2': 0.30, '3': 0.38, '4': 0.48,
                    '5': 0.60, '6': 0.73, '7': 0.85}
        return tab_11_1[zone]

    def calc_z_e(self):
        """
        Определение эквивалентной высоты сооружения
        """
        if self.building_type == 2:
            if self.h <= self.d:
                z_e = array([[0.0, self.h], [self.h, self.h], ])
            elif self.d < self.h <= 2.0 * self.d:
                z_e = array([[0.0, self.d],
                             [(self.h - self.d) * 0.9999, self.d],
                             [self.h - self.d, self.h],
                             [self.h, self.h], ])
            else:
                z_e = array([[0.0, self.d],
                             [self.d, self.d],
                             [self.h - self.d, self.h],
                             [self.h, self.h], ])
        else:
            z_e = array([[0.0, self.h], [self.h, self.h], ])
        return z_e

    @staticmethod
    def calc_k_10(zone_type: str):
        return {'A': 1.0, 'B': 0.65, 'C': 0.4}[zone_type]

    @staticmethod
    def calc_alpha(zone_type: str):
        return {'A': 0.15, 'B': 0.20, 'C': 0.25}[zone_type]

    @staticmethod
    def calc_zeta_10(zone_type: str):
        return {'A': 0.76, 'B': 1.06, 'C': 1.78}[zone_type]

    def calc_k_ze(self, zone_type: str, z_e: array):
        k_10 = self.calc_k_10(zone_type)
        alpha = self.calc_alpha(zone_type)
        k_ze = copy(z_e)
        k_ze[:, 1] = k_10 * (k_ze[:, 1] / 10.0) ** (2.0 * alpha)
        return k_ze

    @staticmethod
    def calc_w_m(w_0: float, k_ze: array, cx: float):
        """
        Определение нормативного значения средней составляющей ветрового давления
        w_0 - нормативное значение ветрового давление
        k_ze - коэффициент учета изменения ветрового давления по высоте (numpy.array)
        cx - аэродинамический коэффициент
        """
        w_m = copy(k_ze)
        w_m[:, 1] = w_0 * w_m[:, 1] * cx
        return w_m

    @staticmethod
    def scheme_d_1_2(w_m: array, g_f: float = 1.4):
        cx = {'A': -1.0, 'B': -0.8, 'C': -0.5, 'D': 0.8, 'E': -0.5}
        d_1_2 = {}
        for key in cx:
            d_1_2[key] = copy(w_m)
            d_1_2[key][:, 1] = d_1_2[key][:, 1] * cx[key] * g_f
        return {'c': cx, 'pressure': d_1_2, }
