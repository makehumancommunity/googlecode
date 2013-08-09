#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

"""

import os
from . import mh

folder = os.path.dirname(__file__)
baseObjFile = os.path.join(folder, "data", "a8_v74.obj")
baseMhcloFile = os.path.join(folder, "data", "a8_v69_clothes.mhclo")
convertMhcloFile = os.path.join(folder, "data", "a8_v69_targets.mhclo")


class CSettings(mh.CSettings):

    def __init__(self, version):
        mh.CSettings.__init__(self, version)

        if version == "alpha7":

            self.irrelevantVerts = {
               "Body" : [(self.vertices["Skirt"][0], self.nTotalVerts)],
               "Skirt" : [(self.nTotalVerts, self.nTotalVerts)],
               "Tights" : [self.vertices["Skirt"]],
            }

            self.affectedVerts = {
                "Body" : (0, self.vertices["Skirt"][0]),
                "Skirt" : self.vertices["Skirt"],
                "Tights" : self.vertices["Tights"],
            }

            self.offsetVerts = {
                "Body" : 0,
                "Skirt" : 0,
                "Tights" : self.vertices["Tights"][0] - self.vertices["Skirt"][0],
            }

            self.skirtWaist =   [15340, 15341, 15736, 15737, 15738, 15739, 15740, 15741, 15742, 15743, 15744, 15745, 15746, 15747, 15748, 15749, 15750, 15751, 15752, 15753, 15754, 15755, ]

            self.tightsWaist =  [16893, 16898, 17824, 17825, 17826, 17827, 17828, 17829, 17830, 17831, 17832, 17833, 17834, 17849, 17864, 17879, 17915, 17916, 17917, 18091, 18096, 18475, ]

            self.XYSkirtColumns = [
              [15340, 15383, 15384, 15427, 15428, 15471, 15472, 15515, 15516, 15559, 15560, 15603, 15604, 15647, 15648, 15691, 15692, 15735, ],
              [15754, 15757, 15794, 15797, 15834, 15837, 15874, 15877, 15914, 15917, 15954, 15957, 15994, 15997, 16034, 16037, 16074, 16077, ],
              [15738, 15773, 15778, 15813, 15818, 15853, 15858, 15893, 15898, 15933, 15938, 15973, 15978, 16013, 16018, 16053, 16058, 16093, ],
              [15737, 15774, 15777, 15814, 15817, 15854, 15857, 15894, 15897, 15934, 15937, 15974, 15977, 16014, 16017, 16054, 16057, 16094, ],
              [15736, 15775, 15776, 15815, 15816, 15855, 15856, 15895, 15896, 15935, 15936, 15975, 15976, 16015, 16016, 16055, 16056, 16095, ],
              [15746, 15765, 15786, 15805, 15826, 15845, 15866, 15885, 15906, 15925, 15946, 15965, 15986, 16005, 16026, 16045, 16066, 16085, ],
              [15740, 15771, 15780, 15811, 15820, 15851, 15860, 15891, 15900, 15931, 15940, 15971, 15980, 16011, 16020, 16051, 16060, 16091, ],
              [15745, 15766, 15785, 15806, 15825, 15846, 15865, 15886, 15905, 15926, 15945, 15966, 15985, 16006, 16025, 16046, 16065, 16086, ],
              [15739, 15772, 15779, 15812, 15819, 15852, 15859, 15892, 15899, 15932, 15939, 15972, 15979, 16012, 16019, 16052, 16059, 16092, ],

              [15741, 15770, 15781, 15810, 15821, 15850, 15861, 15890, 15901, 15930, 15941, 15970, 15981, 16010, 16021, 16050, 16061, 16090, ],
              [15742, 15769, 15782, 15809, 15822, 15849, 15862, 15889, 15902, 15929, 15942, 15969, 15982, 16009, 16022, 16049, 16062, 16089, ],
              [15748, 15763, 15788, 15803, 15828, 15843, 15868, 15883, 15908, 15923, 15948, 15963, 15988, 16003, 16028, 16043, 16068, 16083, ],
              [15747, 15764, 15787, 15804, 15827, 15844, 15867, 15884, 15907, 15924, 15947, 15964, 15987, 16004, 16027, 16044, 16067, 16084, ],
              [15743, 15768, 15783, 15808, 15823, 15848, 15863, 15888, 15903, 15928, 15943, 15968, 15983, 16008, 16023, 16048, 16063, 16088, ],
              [15749, 15762, 15789, 15802, 15829, 15842, 15869, 15882, 15909, 15922, 15949, 15962, 15989, 16002, 16029, 16042, 16069, 16082, ],
              [15744, 15767, 15784, 15807, 15824, 15847, 15864, 15887, 15904, 15927, 15944, 15967, 15984, 16007, 16024, 16047, 16064, 16087, ],
              [15755, 15756, 15795, 15796, 15835, 15836, 15875, 15876, 15915, 15916, 15955, 15956, 15995, 15996, 16035, 16036, 16075, 16076, ],

              [15750, 15761, 15790, 15801, 15830, 15841, 15870, 15881, 15910, 15921, 15950, 15961, 15990, 16001, 16030, 16041, 16070, 16081, ],
              [15751, 15760, 15791, 15800, 15831, 15840, 15871, 15880, 15911, 15920, 15951, 15960, 15991, 16000, 16031, 16040, 16071, 16080, ],
              [15752, 15759, 15792, 15799, 15832, 15839, 15872, 15879, 15912, 15919, 15952, 15959, 15992, 15999, 16032, 16039, 16072, 16079, ],
              [15753, 15758, 15793, 15798, 15833, 15838, 15873, 15878, 15913, 15918, 15953, 15958, 15993, 15998, 16033, 16038, 16073, 16078, ],
              [15341, 15382, 15385, 15426, 15429, 15470, 15473, 15514, 15517, 15558, 15561, 15602, 15605, 15646, 15649, 15690, 15693, 15734, ],
            ]

            self.ZSkirtRows = [
              [15472, 15473, 15856, 15857, 15858, 15859, 15860, 15861, 15862, 15863, 15864, 15865, 15866, 15867, 15868, 15869, 15870, 15871, 15872, 15873, 15874, 15875, ],
              [15514, 15515, 15876, 15877, 15878, 15879, 15880, 15881, 15882, 15883, 15884, 15885, 15886, 15887, 15888, 15889, 15890, 15891, 15892, 15893, 15894, 15895, ],
              [15516, 15517, 15896, 15897, 15898, 15899, 15900, 15901, 15902, 15903, 15904, 15905, 15906, 15907, 15908, 15909, 15910, 15911, 15912, 15913, 15914, 15915, ],
              [15558, 15559, 15916, 15917, 15918, 15919, 15920, 15921, 15922, 15923, 15924, 15925, 15926, 15927, 15928, 15929, 15930, 15931, 15932, 15933, 15934, 15935, ],
              [15560, 15561, 15936, 15937, 15938, 15939, 15940, 15941, 15942, 15943, 15944, 15945, 15946, 15947, 15948, 15949, 15950, 15951, 15952, 15953, 15954, 15955, ],
              [15602, 15603, 15956, 15957, 15958, 15959, 15960, 15961, 15962, 15963, 15964, 15965, 15966, 15967, 15968, 15969, 15970, 15971, 15972, 15973, 15974, 15975, ],
              [15604, 15605, 15976, 15977, 15978, 15979, 15980, 15981, 15982, 15983, 15984, 15985, 15986, 15987, 15988, 15989, 15990, 15991, 15992, 15993, 15994, 15995, ],
              [15646, 15647, 15996, 15997, 15998, 15999, 16000, 16001, 16002, 16003, 16004, 16005, 16006, 16007, 16008, 16009, 16010, 16011, 16012, 16013, 16014, 16015, ],
              [15648, 15649, 16016, 16017, 16018, 16019, 16020, 16021, 16022, 16023, 16024, 16025, 16026, 16027, 16028, 16029, 16030, 16031, 16032, 16033, 16034, 16035, ],
              [15690, 15691, 16036, 16037, 16038, 16039, 16040, 16041, 16042, 16043, 16044, 16045, 16046, 16047, 16048, 16049, 16050, 16051, 16052, 16053, 16054, 16055, ],
              [15692, 15693, 16056, 16057, 16058, 16059, 16060, 16061, 16062, 16063, 16064, 16065, 16066, 16067, 16068, 16069, 16070, 16071, 16072, 16073, 16074, 16075, ],
              [15734, 15735, 16076, 16077, 16078, 16079, 16080, 16081, 16082, 16083, 16084, 16085, 16086, 16087, 16088, 16089, 16090, 16091, 16092, 16093, 16094, 16095, ],
            ]

        elif version == "alpha8a":

            self.irrelevantVerts = {
               "Body" :     [(self.vertices["Penis"][0], self.nTotalVerts)],
               "Penis" :     [(self.vertices["Penis"][1], self.nTotalVerts)],
               "Tights" :   [self.vertices["Penis"], (self.vertices["Tights"][1], self.nTotalVerts)],
               "Skirt" :    [self.vertices["Penis"], (self.vertices["Skirt"][1], self.nTotalVerts)],
               "Hair" :     [self.vertices["Penis"], (self.vertices["Hair"][1], self.nTotalVerts)],
            }

            self.affectedVerts = {
                "Body" : (0, self.vertices["Penis"][0]),
                "Penis" : self.vertices["Penis"],
                "Tights" : self.vertices["Tights"],
                "Skirt" : self.vertices["Skirt"],
                "Hair" : self.vertices["Hair"],
            }

            penis = self.vertices["Penis"][1] - self.vertices["Penis"][0]
            self.offsetVerts = {
                "Body" : 0,
                "Penis" : 0,
                "Tights" : penis,
                "Skirt" : penis,
                "Hair" : penis,
            }

            self.skirtWaist = [18025, 18026, 18021, 18027, 18028, 18023, 18022, 18053, 18020, 18089, 18057, 18058, 18063, 18062, 18056, 18061, 18059, 18060, 18024, 18029, 18019, 18039, 18030, 18031, 18032, 18033, 18050, 18034, 18086, 18068, 18067, 18066, 18065, 18074, 18055, 18064, ]

            self.tightsWaist = [16053, 16054, 16049, 16055, 16056, 16051, 16050, 16544, 17363, 17878, 17377, 17378, 17383, 17382, 17376, 17381, 17379, 17380, 16052, 16058, 15789, 16072, 16063, 16064, 16065, 16066, 16526, 17394, 17860, 17393, 17392, 17391, 17390, 17400, 17106, 17385, ]

            self.XYSkirtColumns = [
                [18260, 18296, 18332, 18368, 18404, 18440, 18476, 18512, 18548, 18584, 18620, 18656, 18692, 18728, ],
                [18269, 18305, 18341, 18377, 18413, 18449, 18485, 18521, 18557, 18593, 18629, 18665, 18701, 18737, ],
                [18259, 18295, 18331, 18367, 18403, 18439, 18475, 18511, 18547, 18583, 18619, 18655, 18691, 18727, ],
                [18262, 18298, 18334, 18370, 18406, 18442, 18478, 18514, 18550, 18586, 18622, 18658, 18694, 18730, ],
                [18258, 18294, 18330, 18366, 18402, 18438, 18474, 18510, 18546, 18582, 18618, 18654, 18690, 18726, ],
                [18257, 18293, 18329, 18365, 18401, 18437, 18473, 18509, 18545, 18581, 18617, 18653, 18689, 18725, ],
                [18261, 18297, 18333, 18369, 18405, 18441, 18477, 18513, 18549, 18585, 18621, 18657, 18693, 18729, ],
                [18266, 18302, 18338, 18374, 18410, 18446, 18482, 18518, 18554, 18590, 18626, 18662, 18698, 18734, ],
                [18267, 18303, 18339, 18375, 18411, 18447, 18483, 18519, 18555, 18591, 18627, 18663, 18699, 18735, ],
                [18265, 18301, 18337, 18373, 18409, 18445, 18481, 18517, 18553, 18589, 18625, 18661, 18697, 18733, ],
                [18264, 18300, 18336, 18372, 18408, 18444, 18480, 18516, 18552, 18588, 18624, 18660, 18696, 18732, ],
                [18251, 18287, 18323, 18359, 18395, 18431, 18467, 18503, 18539, 18575, 18611, 18647, 18683, 18719, ],
                [18263, 18299, 18335, 18371, 18407, 18443, 18479, 18515, 18551, 18587, 18623, 18659, 18695, 18731, ],
                [18252, 18288, 18324, 18360, 18396, 18432, 18468, 18504, 18540, 18576, 18612, 18648, 18684, 18720, ],
                [18253, 18289, 18325, 18361, 18397, 18433, 18469, 18505, 18541, 18577, 18613, 18649, 18685, 18721, ],
                [18254, 18290, 18326, 18362, 18398, 18434, 18470, 18506, 18542, 18578, 18614, 18650, 18686, 18722, ],
                [18255, 18291, 18327, 18363, 18399, 18435, 18471, 18507, 18543, 18579, 18615, 18651, 18687, 18723, ],
                [18268, 18304, 18340, 18376, 18412, 18448, 18484, 18520, 18556, 18592, 18628, 18664, 18700, 18736, ],
                [18256, 18292, 18328, 18364, 18400, 18436, 18472, 18508, 18544, 18580, 18616, 18652, 18688, 18724, ],
            ]

            self.ZSkirtRows = [
                [18702, 18703, 18704, 18705, 18706, 18707, 18708, 18709, 18710, 18711, 18712, 18713, 18714, 18715, 18716, 18717, 18718, 18719, 18720, 18721, 18722, 18723, 18724, 18725, 18726, 18727, 18728, 18729, 18730, 18731, 18732, 18733, 18734, 18735, 18736, 18737, ],
                [18666, 18667, 18668, 18669, 18670, 18671, 18672, 18673, 18674, 18675, 18676, 18677, 18678, 18679, 18680, 18681, 18682, 18683, 18684, 18685, 18686, 18687, 18688, 18689, 18690, 18691, 18692, 18693, 18694, 18695, 18696, 18697, 18698, 18699, 18700, 18701, ],
                [18630, 18631, 18632, 18633, 18634, 18635, 18636, 18637, 18638, 18639, 18640, 18641, 18642, 18643, 18644, 18645, 18646, 18647, 18648, 18649, 18650, 18651, 18652, 18653, 18654, 18655, 18656, 18657, 18658, 18659, 18660, 18661, 18662, 18663, 18664, 18665, ],
                [18594, 18595, 18596, 18597, 18598, 18599, 18600, 18601, 18602, 18603, 18604, 18605, 18606, 18607, 18608, 18609, 18610, 18611, 18612, 18613, 18614, 18615, 18616, 18617, 18618, 18619, 18620, 18621, 18622, 18623, 18624, 18625, 18626, 18627, 18628, 18629, ],
                [18558, 18559, 18560, 18561, 18562, 18563, 18564, 18565, 18566, 18567, 18568, 18569, 18570, 18571, 18572, 18573, 18574, 18575, 18576, 18577, 18578, 18579, 18580, 18581, 18582, 18583, 18584, 18585, 18586, 18587, 18588, 18589, 18590, 18591, 18592, 18593, ],
                [18522, 18523, 18524, 18525, 18526, 18527, 18528, 18529, 18530, 18531, 18532, 18533, 18534, 18535, 18536, 18537, 18538, 18539, 18540, 18541, 18542, 18543, 18544, 18545, 18546, 18547, 18548, 18549, 18550, 18551, 18552, 18553, 18554, 18555, 18556, 18557, ],
                [18486, 18487, 18488, 18489, 18490, 18491, 18492, 18493, 18494, 18495, 18496, 18497, 18498, 18499, 18500, 18501, 18502, 18503, 18504, 18505, 18506, 18507, 18508, 18509, 18510, 18511, 18512, 18513, 18514, 18515, 18516, 18517, 18518, 18519, 18520, 18521, ],
                [18450, 18451, 18452, 18453, 18454, 18455, 18456, 18457, 18458, 18459, 18460, 18461, 18462, 18463, 18464, 18465, 18466, 18467, 18468, 18469, 18470, 18471, 18472, 18473, 18474, 18475, 18476, 18477, 18478, 18479, 18480, 18481, 18482, 18483, 18484, 18485, ],
                [18414, 18415, 18416, 18417, 18418, 18419, 18420, 18421, 18422, 18423, 18424, 18425, 18426, 18427, 18428, 18429, 18430, 18431, 18432, 18433, 18434, 18435, 18436, 18437, 18438, 18439, 18440, 18441, 18442, 18443, 18444, 18445, 18446, 18447, 18448, 18449, ],
                [18378, 18379, 18380, 18381, 18382, 18383, 18384, 18385, 18386, 18387, 18388, 18389, 18390, 18391, 18392, 18393, 18394, 18395, 18396, 18397, 18398, 18399, 18400, 18401, 18402, 18403, 18404, 18405, 18406, 18407, 18408, 18409, 18410, 18411, 18412, 18413, ]
            ]

        elif version == "alpha8b":

            self.irrelevantVerts = {
               "Body" :     [(self.vertices["Penis"][0], self.nTotalVerts)],
               "Penis" :     [(self.vertices["Penis"][1], self.nTotalVerts)],
               "Tights" :   [self.vertices["Penis"], (self.vertices["Tights"][1], self.nTotalVerts)],
               "Skirt" :    [self.vertices["Penis"], (self.vertices["Skirt"][1], self.nTotalVerts)],
               "Hair" :     [self.vertices["Penis"], (self.vertices["Hair"][1], self.nTotalVerts)],
            }

            self.affectedVerts = {
                "Body" : (0, self.vertices["Penis"][0]),
                "Penis" : self.vertices["Penis"],
                "Tights" : self.vertices["Tights"],
                "Skirt" : self.vertices["Skirt"],
                "Hair" : self.vertices["Hair"],
            }

            penis = self.vertices["Penis"][1] - self.vertices["Penis"][0]
            self.offsetVerts = {
                "Body" : 0,
                "Penis" : 0,
                "Tights" : penis,
                "Skirt" : penis,
                "Hair" : penis,
            }

            self.skirtWaist = [18009, 18010, 18005, 18011, 18012, 18007, 18006, 18037, 18004, 18073, 18041, 18042, 18047, 18046, 18040, 18045, 18043, 18044, 18008, 18013, 18003, 18023, 18014, 18015, 18016, 18017, 18034, 18018, 18070, 18052, 18051, 18050, 18049, 18058, 18039, 18048]

            self.tightsWaist = [16037, 16038, 16033, 16039, 16040, 16035, 16034, 16528, 17347, 17862, 17361, 17362, 17367, 17366, 17360, 17365, 17363, 17364, 16036, 16042, 15773, 16056, 16047, 16048, 16049, 16050, 16510, 17378, 17844, 17377, 17376, 17375, 17374, 17384, 17090, 17369]

            self.XYSkirtColumns = [
                [18244, 18280, 18316, 18352, 18388, 18424, 18460, 18496, 18532, 18568, 18604, 18640, 18676, 18712],
                [18253, 18289, 18325, 18361, 18397, 18433, 18469, 18505, 18541, 18577, 18613, 18649, 18685, 18721],
                [18243, 18279, 18315, 18351, 18387, 18423, 18459, 18495, 18531, 18567, 18603, 18639, 18675, 18711],
                [18246, 18282, 18318, 18354, 18390, 18426, 18462, 18498, 18534, 18570, 18606, 18642, 18678, 18714],
                [18242, 18278, 18314, 18350, 18386, 18422, 18458, 18494, 18530, 18566, 18602, 18638, 18674, 18710],
                [18241, 18277, 18313, 18349, 18385, 18421, 18457, 18493, 18529, 18565, 18601, 18637, 18673, 18709],
                [18245, 18281, 18317, 18353, 18389, 18425, 18461, 18497, 18533, 18569, 18605, 18641, 18677, 18713],
                [18250, 18286, 18322, 18358, 18394, 18430, 18466, 18502, 18538, 18574, 18610, 18646, 18682, 18718],
                [18251, 18287, 18323, 18359, 18395, 18431, 18467, 18503, 18539, 18575, 18611, 18647, 18683, 18719],
                [18249, 18285, 18321, 18357, 18393, 18429, 18465, 18501, 18537, 18573, 18609, 18645, 18681, 18717],
                [18248, 18284, 18320, 18356, 18392, 18428, 18464, 18500, 18536, 18572, 18608, 18644, 18680, 18716],
                [18235, 18271, 18307, 18343, 18379, 18415, 18451, 18487, 18523, 18559, 18595, 18631, 18667, 18703],
                [18247, 18283, 18319, 18355, 18391, 18427, 18463, 18499, 18535, 18571, 18607, 18643, 18679, 18715],
                [18236, 18272, 18308, 18344, 18380, 18416, 18452, 18488, 18524, 18560, 18596, 18632, 18668, 18704],
                [18237, 18273, 18309, 18345, 18381, 18417, 18453, 18489, 18525, 18561, 18597, 18633, 18669, 18705],
                [18238, 18274, 18310, 18346, 18382, 18418, 18454, 18490, 18526, 18562, 18598, 18634, 18670, 18706],
                [18239, 18275, 18311, 18347, 18383, 18419, 18455, 18491, 18527, 18563, 18599, 18635, 18671, 18707],
                [18252, 18288, 18324, 18360, 18396, 18432, 18468, 18504, 18540, 18576, 18612, 18648, 18684, 18720],
                [18240, 18276, 18312, 18348, 18384, 18420, 18456, 18492, 18528, 18564, 18600, 18636, 18672, 18708],
            ]

            self.ZSkirtRows = [
                [18686, 18687, 18688, 18689, 18690, 18691, 18692, 18693, 18694, 18695, 18696, 18697, 18698, 18699, 18700, 18701, 18702, 18703, 18704, 18705, 18706, 18707, 18708, 18709, 18710, 18711, 18712, 18713, 18714, 18715, 18716, 18717, 18718, 18719, 18720, 18721],
                [18650, 18651, 18652, 18653, 18654, 18655, 18656, 18657, 18658, 18659, 18660, 18661, 18662, 18663, 18664, 18665, 18666, 18667, 18668, 18669, 18670, 18671, 18672, 18673, 18674, 18675, 18676, 18677, 18678, 18679, 18680, 18681, 18682, 18683, 18684, 18685],
                [18614, 18615, 18616, 18617, 18618, 18619, 18620, 18621, 18622, 18623, 18624, 18625, 18626, 18627, 18628, 18629, 18630, 18631, 18632, 18633, 18634, 18635, 18636, 18637, 18638, 18639, 18640, 18641, 18642, 18643, 18644, 18645, 18646, 18647, 18648, 18649],
                [18578, 18579, 18580, 18581, 18582, 18583, 18584, 18585, 18586, 18587, 18588, 18589, 18590, 18591, 18592, 18593, 18594, 18595, 18596, 18597, 18598, 18599, 18600, 18601, 18602, 18603, 18604, 18605, 18606, 18607, 18608, 18609, 18610, 18611, 18612, 18613],
                [18542, 18543, 18544, 18545, 18546, 18547, 18548, 18549, 18550, 18551, 18552, 18553, 18554, 18555, 18556, 18557, 18558, 18559, 18560, 18561, 18562, 18563, 18564, 18565, 18566, 18567, 18568, 18569, 18570, 18571, 18572, 18573, 18574, 18575, 18576, 18577],
                [18506, 18507, 18508, 18509, 18510, 18511, 18512, 18513, 18514, 18515, 18516, 18517, 18518, 18519, 18520, 18521, 18522, 18523, 18524, 18525, 18526, 18527, 18528, 18529, 18530, 18531, 18532, 18533, 18534, 18535, 18536, 18537, 18538, 18539, 18540, 18541],
                [18470, 18471, 18472, 18473, 18474, 18475, 18476, 18477, 18478, 18479, 18480, 18481, 18482, 18483, 18484, 18485, 18486, 18487, 18488, 18489, 18490, 18491, 18492, 18493, 18494, 18495, 18496, 18497, 18498, 18499, 18500, 18501, 18502, 18503, 18504, 18505],
                [18434, 18435, 18436, 18437, 18438, 18439, 18440, 18441, 18442, 18443, 18444, 18445, 18446, 18447, 18448, 18449, 18450, 18451, 18452, 18453, 18454, 18455, 18456, 18457, 18458, 18459, 18460, 18461, 18462, 18463, 18464, 18465, 18466, 18467, 18468, 18469],
                [18398, 18399, 18400, 18401, 18402, 18403, 18404, 18405, 18406, 18407, 18408, 18409, 18410, 18411, 18412, 18413, 18414, 18415, 18416, 18417, 18418, 18419, 18420, 18421, 18422, 18423, 18424, 18425, 18426, 18427, 18428, 18429, 18430, 18431, 18432, 18433],
                [18362, 18363, 18364, 18365, 18366, 18367, 18368, 18369, 18370, 18371, 18372, 18373, 18374, 18375, 18376, 18377, 18378, 18379, 18380, 18381, 18382, 18383, 18384, 18385, 18386, 18387, 18388, 18389, 18390, 18391, 18392, 18393, 18394, 18395, 18396, 18397],
            ]


settings = {
    "alpha7" : CSettings("alpha7"),
    "alpha8" : CSettings("alpha8b"),
    "None"   : None
}

