#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Gizmos used by mhx rig
"""

def asString():
    return(

"""
# ----------------------------- MESH --------------------- # 

Mesh GZM_FootCtrl_L GZM_FootCtrl_L 
  Verts
    v 0.275 1.535 -0.077 ;
    v 0.275 1.106 -0.073 ;
    v 0.275 -0.482 -0.057 ;
    v -0.286 -0.482 -0.057 ;
    v -0.286 -0.482 -0.057 ;
    v -0.286 1.106 -0.073 ;
    v -0.286 1.535 -0.077 ;
    v 0.032 1.752 0.184 ;
    v 0.272 -0.482 -0.057 ;
    v 0.275 -0.467 -0.057 ;
    v -0.286 -0.467 -0.057 ;
  end Verts
  Edges
    e 0 1 ;
    e 3 4 ;
    e 5 6 ;
    e 6 7 ;
    e 0 7 ;
    e 2 8 ;
    e 3 8 ;
    e 1 9 ;
    e 2 9 ;
    e 4 10 ;
    e 5 10 ;
  end Edges
end Mesh

Object GZM_FootCtrl_L MESH GZM_FootCtrl_L
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object

Mesh GZM_WristCtrl_L GZM_WristCtrl_L 
  Verts
    v 0.0651361 0.0105648 0.136498 ;
    v 0.0608409 -0.00617499 -0.122574 ;
    v 0.00624153 0.0126274 0.177229 ;
    v 0.000629619 -0.00924418 -0.161265 ;
    v -0.0637748 0.0129347 0.192377 ;
    v -0.069849 -0.0107389 -0.174007 ;
    v -0.134253 0.01144 0.179635 ;
    v -0.139865 -0.0104316 -0.158859 ;
    v -0.194465 0.00837081 0.140944 ;
    v -0.19876 -0.00836897 -0.118128 ;
    v -0.24243 0.00335172 0.070186 ;
    v -0.244352 -0.00414057 -0.0457679 ;
    v 0.116754 0.0026493 0.00604154 ;
    v 0.103943 0.00706096 0.0763855 ;
    v 0.101618 -0.00199856 -0.0638238 ;
    v -0.29135 0.0027428 0.0679912 ;
    v -0.293172 -0.00435769 -0.0418993 ;
    v -0.406267 -0.00177098 0.0149983 ;
    v -0.287616 0.00818811 0.151919 ;
    v -0.292222 -0.00976342 -0.125907 ;
  end Verts
  Edges
    e 0 2 ;
    e 1 3 ;
    e 2 4 ;
    e 3 5 ;
    e 4 6 ;
    e 5 7 ;
    e 6 8 ;
    e 7 9 ;
    e 8 10 ;
    e 9 11 ;
    e 12 13 ;
    e 12 14 ;
    e 0 13 ;
    e 1 14 ;
    e 10 15 ;
    e 11 16 ;
    e 17 18 ;
    e 17 19 ;
    e 15 18 ;
    e 16 19 ;
  end Edges
end Mesh

Object GZM_WristCtrl_L MESH GZM_WristCtrl_L
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object


# ----------------------------- MESH --------------------- # 

Mesh GZM_WristCtrl_R GZM_WristCtrl_R 
  Verts
    v -0.0837871 0.0105648 -0.118128 ;
    v -0.0794919 -0.00617498 0.140944 ;
    v -0.0248925 0.0126274 -0.158859 ;
    v -0.0192806 -0.00924417 0.179635 ;
    v 0.0451238 0.0129347 -0.174007 ;
    v 0.0511981 -0.0107389 0.192377 ;
    v 0.115602 0.01144 -0.161265 ;
    v 0.121214 -0.0104315 0.177229 ;
    v 0.175814 0.0083708 -0.122574 ;
    v 0.180109 -0.00836896 0.136498 ;
    v 0.223779 0.00335171 -0.0518158 ;
    v 0.225701 -0.00414056 0.0641382 ;
    v -0.135405 0.0026493 0.0123287 ;
    v -0.122594 0.00706095 -0.0580152 ;
    v -0.120269 -0.00199856 0.082194 ;
    v 0.272699 0.0027428 -0.0496209 ;
    v 0.274521 -0.00435769 0.0602695 ;
    v 0.387617 -0.00177098 0.00337188 ;
    v 0.268965 0.0081881 -0.133549 ;
    v 0.273571 -0.00976341 0.144277 ;
  end Verts
  Edges
    e 0 2 ;
    e 1 3 ;
    e 2 4 ;
    e 3 5 ;
    e 4 6 ;
    e 5 7 ;
    e 6 8 ;
    e 7 9 ;
    e 8 10 ;
    e 9 11 ;
    e 12 13 ;
    e 12 14 ;
    e 0 13 ;
    e 1 14 ;
    e 10 15 ;
    e 11 16 ;
    e 17 18 ;
    e 17 19 ;
    e 15 18 ;
    e 16 19 ;
  end Edges
end Mesh

Object GZM_WristCtrl_R MESH GZM_WristCtrl_R
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object

# ----------------------------- MESH --------------------- # 

Mesh GZM_RevFoot GZM_RevFoot 
  Verts
    v -0.247 0.987 0.212 ;
    v -0.248 0.165 0.341 ;
    v 0.287 0.165 0.341 ;
    v 0.287 0.987 0.212 ;
    v -0.247 0.682 -0.505 ;
    v -0.247 -0.020 -0.095 ;
    v 0.287 -0.021 -0.095 ;
    v 0.288 0.682 -0.505 ;
  end Verts
  Faces
    f 0 1 2 3 ;
    f 4 7 6 5 ;
    f 0 4 5 1 ;
    f 1 5 6 2 ;
    f 2 6 7 3 ;
    f 4 0 3 7 ;
  end Faces
end Mesh

Object GZM_RevFoot MESH GZM_RevFoot
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
  parent Refer Object CustomShapes ;
end Object
# ----------------------------- MESH --------------------- # 

Mesh GZM_RevToe GZM_RevToe 
  Verts
    v 0.465 1.004 -0.193 ;
    v 0.463 -0.258 -0.151 ;
    v -0.464 -0.257 -0.152 ;
    v -0.463 1.005 -0.194 ;
    v 0.464 0.955 0.595 ;
    v 0.463 -0.295 0.322 ;
    v -0.465 -0.295 0.321 ;
    v -0.464 0.956 0.594 ;
  end Verts
  Faces
    f 0 1 2 3 ;
    f 4 7 6 5 ;
    f 0 4 5 1 ;
    f 1 5 6 2 ;
    f 2 6 7 3 ;
    f 4 0 3 7 ;
  end Faces
end Mesh

Object GZM_RevToe MESH GZM_RevToe
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
  parent Refer Object CustomShapes ;
end Object

# ----------------------------- MESH --------------------- # 

Mesh GZM_IK_Shoulder GZM_IK_Shoulder 
  Verts
    v -0.000123143 -0.487691 1.74227 ;
    v -0.000123253 -3.34246 2.74369 ;
    v -0.000123253 -0.269723 2.74369 ;
    v -0.000123474 -1.80609 4.28006 ;
    v -0.000123253 -2.31822 2.74369 ;
    v -0.000123253 -1.29397 2.74369 ;
    v -0.000123253 -0.29533 2.7693 ;
    v -0.000123474 -1.78049 4.25446 ;
    v -0.000123253 -3.31686 2.7693 ;
    v -0.000123474 -1.8317 4.25446 ;
    v -0.000123253 -3.30832 2.74369 ;
    v -0.000123253 -2.35236 2.74369 ;
    v -0.000123253 -0.303865 2.74369 ;
    v -0.000123253 -1.25983 2.74369 ;
    v -0.000123253 -1.29397 2.71809 ;
    v -0.000123253 -2.31822 2.71809 ;
    v -0.000123143 -1.29397 2.11238 ;
    v -0.000123143 -2.31822 2.11238 ;
    v -0.000123143 -1.29397 2.14116 ;
    v -0.000123143 -2.31822 2.14116 ;
    v -0.000123143 -1.27233 2.10037 ;
    v -0.000123143 -2.34195 2.10037 ;
    v -0.000122812 -1.27442 -1.44868 ;
    v -0.000122812 -2.34405 -1.44868 ;
    v -0.000122812 -1.29815 -1.48947 ;
    v -0.000122812 -2.3224 -1.48947 ;
    v -0.000122812 -1.29815 -1.46069 ;
    v -0.000122812 -2.3224 -1.46069 ;
    v -0.000122812 -1.29815 -2.0664 ;
    v -0.000122812 -2.3224 -2.0664 ;
    v -0.000122812 -2.35654 -2.09201 ;
    v -0.000122812 -3.31251 -2.09201 ;
    v -0.000122812 -1.26401 -2.09201 ;
    v -0.000122812 -0.308048 -2.09201 ;
    v -0.000122592 -1.78467 -3.60277 ;
    v -0.000122812 -0.299513 -2.11762 ;
    v -0.000122592 -1.83588 -3.60277 ;
    v -0.000122812 -3.32104 -2.11761 ;
    v -0.000122812 -2.3224 -2.09201 ;
    v -0.000122812 -1.29815 -2.09201 ;
    v -0.000122592 -1.81028 -3.62838 ;
    v -0.000122812 -3.34665 -2.09201 ;
    v -0.000122812 -0.273908 -2.09201 ;
    v -0.000122922 -0.487723 -1.09062 ;
    v -0.000123143 -3.22462 1.74231 ;
    v -0.000122922 -3.22462 -1.09062 ;
    v -0.000122986 0.194974 0.325864 ;
    v -0.000122922 -0.175975 -0.551507 ;
    v -0.000123033 -0.174496 1.20171 ;
    v -0.000123033 -3.53661 1.20171 ;
    v -0.000122922 -3.53513 -0.551507 ;
    v -0.000122986 -3.90608 0.325864 ;
  end Verts
  Edges
    e 2 6 ;
    e 6 7 ;
    e 3 7 ;
    e 1 8 ;
    e 8 9 ;
    e 3 9 ;
    e 1 10 ;
    e 10 11 ;
    e 4 11 ;
    e 2 12 ;
    e 12 13 ;
    e 5 13 ;
    e 5 14 ;
    e 4 15 ;
    e 14 18 ;
    e 16 18 ;
    e 15 19 ;
    e 17 19 ;
    e 0 20 ;
    e 16 20 ;
    e 17 21 ;
    e 22 26 ;
    e 23 27 ;
    e 24 26 ;
    e 24 28 ;
    e 25 27 ;
    e 25 29 ;
    e 28 39 ;
    e 29 38 ;
    e 30 38 ;
    e 30 31 ;
    e 31 41 ;
    e 32 39 ;
    e 32 33 ;
    e 33 42 ;
    e 34 40 ;
    e 34 35 ;
    e 35 42 ;
    e 36 40 ;
    e 36 37 ;
    e 37 41 ;
    e 23 45 ;
    e 22 43 ;
    e 21 44 ;
    e 46 48 ;
    e 46 47 ;
    e 0 48 ;
    e 43 47 ;
    e 50 51 ;
    e 49 51 ;
    e 44 49 ;
    e 45 50 ;
  end Edges
end Mesh

Object GZM_IK_Shoulder MESH GZM_IK_Shoulder
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object

Mesh GZM_Root GZM_Root 
  Verts
    v -1.734 -2.301 0 ;
    v -2.387 -1.648 0 ;
    v -2.806 -0.825 0 ;
    v -3.717 0.086 0 ;
    v -2.806 0.997 0 ;
    v -2.387 1.820 0 ;
    v -1.734 2.473 0 ;
    v -0.911 2.862 0 ;
    v 0 3.103 0 ;
    v 0.911 2.862 0 ;
    v 1.734 2.473 0 ;
    v 2.387 1.820 0 ;
    v 2.806 0.997 0 ;
    v 3.717 0.086 0 ;
    v 2.806 -0.825 0 ;
    v 2.387 -1.648 0 ;
    v 1.734 -2.301 0 ;
    v 0.913 -2.720 0 ;
    v -0 -5.166 0 ;
    v -0.913 -2.720 0 ;
    v -3.261 -0.370 0 ;
    v -3.261 0.542 0 ;
    v -0.456 2.989 0 ;
    v 0.456 2.989 0 ;
    v 3.261 0.542 0 ;
    v 3.261 -0.370 0 ;
    v 0.654 -3.486 0 ;
    v -0.654 -3.486 0 ;
    v -3.489 -0.142 0 ;
    v -3.489 0.314 0 ;
    v -0.228 3.051 0 ;
    v 0.228 3.051 0 ;
    v 3.489 0.314 0 ;
    v 3.489 -0.142 0 ;
    v 0.327 -4.419 0 ;
    v -0.327 -4.419 0 ;
    v 0 0.086 0 ;
    v -3.654 0.086 0 ;
    v 3.654 0.086 0 ;
    v 0 3.148 0 ;
    v -1.827 0.086 0 ;
    v 1.827 0.086 0 ;
    v 0 1.913 0 ;
  end Verts
  Edges
    e 0 1 ;
    e 1 2 ;
    e 4 5 ;
    e 5 6 ;
    e 6 7 ;
    e 9 10 ;
    e 10 11 ;
    e 11 12 ;
    e 14 15 ;
    e 15 16 ;
    e 16 17 ;
    e 0 19 ;
    e 2 20 ;
    e 4 21 ;
    e 7 22 ;
    e 9 23 ;
    e 12 24 ;
    e 14 25 ;
    e 17 26 ;
    e 19 27 ;
    e 20 28 ;
    e 3 28 ;
    e 21 29 ;
    e 3 29 ;
    e 22 30 ;
    e 8 30 ;
    e 8 31 ;
    e 23 31 ;
    e 24 32 ;
    e 13 32 ;
    e 25 33 ;
    e 13 33 ;
    e 18 34 ;
    e 26 34 ;
    e 18 35 ;
    e 27 35 ;
    e 3 37 ;
    e 13 38 ;
    e 8 39 ;
    e 2 4 ;
    e 17 19 ;
    e 12 14 ;
    e 7 9 ;
    e 36 40 ;
    e 36 41 ;
    e 36 42 ;
  end Edges
end Mesh

Object GZM_Root MESH GZM_Root
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 1 ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object

# ----------------------------- MESH --------------------- # 

Mesh GZM_Knuckle GZM_Knuckle 
  Verts
    v 5.25864e-09 -0.166374 0.0882252 ;
    v 5.25864e-09 -0.163177 0.120683 ;
    v 5.25864e-09 -0.153709 0.151894 ;
    v -4.658e-09 -0.138335 0.180657 ;
    v 5.25864e-09 -0.117644 0.205869 ;
    v 1.51753e-08 -0.0924322 0.22656 ;
    v 1.0217e-08 -0.0636684 0.241934 ;
    v 1.26961e-08 -0.0324578 0.251402 ;
    v 5.25864e-09 5.42114e-08 0.254599 ;
    v 1.76544e-08 0.0324579 0.251402 ;
    v 2.01336e-08 0.0636685 0.241934 ;
    v 1.51753e-08 0.0924323 0.22656 ;
    v 2.50919e-08 0.117644 0.205869 ;
    v 1.51753e-08 0.138335 0.180657 ;
    v 1.51753e-08 0.153709 0.151893 ;
    v 1.51753e-08 0.980272 0.15318 ;
    v 5.25864e-09 0.983469 -0.000996985 ;
    v 5.25864e-09 -0.166374 0.00495131 ;
  end Verts
  Edges
    e 0 1 ;
    e 1 2 ;
    e 2 3 ;
    e 3 4 ;
    e 4 5 ;
    e 5 6 ;
    e 6 7 ;
    e 7 8 ;
    e 8 9 ;
    e 9 10 ;
    e 10 11 ;
    e 11 12 ;
    e 12 13 ;
    e 13 14 ;
    e 14 15 ;
    e 15 16 ;
    e 0 17 ;
  end Edges
end Mesh

Object GZM_Knuckle MESH GZM_Knuckle
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
  parent Refer Object CustomShapes ;
end Object

# ----------------------------- MESH --------------------- # 

Mesh GZM_FootCtrl_R GZM_FootCtrl_R 
  Verts
    v -0.265 1.534 -0.081 ;
    v -0.265 1.106 -0.074 ;
    v -0.265 -0.483 -0.050 ;
    v 0.297 -0.483 -0.050 ;
    v 0.297 -0.483 -0.050 ;
    v 0.297 1.106 -0.074 ;
    v 0.297 1.534 -0.081 ;
    v -0.021 1.753 0.179 ;
    v -0.261 -0.483 -0.050 ;
    v -0.265 -0.467 -0.051 ;
    v 0.297 -0.467 -0.051 ;
  end Verts
  Edges
    e 0 1 ;
    e 3 4 ;
    e 5 6 ;
    e 6 7 ;
    e 0 7 ;
    e 2 8 ;
    e 3 8 ;
    e 1 9 ;
    e 2 9 ;
    e 4 10 ;
    e 5 10 ;
  end Edges
end Mesh

Object GZM_FootCtrl_R MESH GZM_FootCtrl_R
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object

# ----------------------------- MESH --------------------- # 

Mesh GZM_HandCtrl_L GZM_HandCtrl_L 
  Verts
    v -0.872067 2.19592 -0.135049 ;
    v -1.1297 1.09254 -0.135049 ;
    v -1.1297 -0.210723 -0.135048 ;
    v -0.13363 -0.894258 1.42677 ;
    v 1.15155 -0.210723 -0.135049 ;
    v 1.15155 1.09254 -0.135049 ;
    v 0.980654 2.68743 -0.135049 ;
    v -0.133633 2.68743 -0.135049 ;
  end Verts
  Edges
    e 4 5 ;
    e 5 6 ;
    e 6 7 ;
    e 0 7 ;
    e 0 1 ;
    e 1 2 ;
    e 2 3 ;
    e 3 4 ;
  end Edges
end Mesh

Object GZM_HandCtrl_L MESH GZM_HandCtrl_L
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object


# ----------------------------- MESH --------------------- # 

Mesh GZM_HandCtrl_R GZM_HandCtrl_R 
  Verts
    v 0.938468 2.21718 -0.135049 ;
    v 1.1961 1.11379 -0.135049 ;
    v 1.1961 -0.189469 -0.135049 ;
    v 0.200033 -0.873004 1.42677 ;
    v -1.08515 -0.18947 -0.135049 ;
    v -1.08515 1.11379 -0.135049 ;
    v -0.914253 2.70868 -0.135049 ;
    v 0.200035 2.70868 -0.135049 ;
  end Verts
  Edges
    e 4 5 ;
    e 5 6 ;
    e 6 7 ;
    e 0 7 ;
    e 0 1 ;
    e 1 2 ;
    e 2 3 ;
    e 3 4 ;
  end Edges
end Mesh

Object GZM_HandCtrl_R MESH GZM_HandCtrl_R
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
    Modifier Subsurf SUBSURF
      levels 2 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
  parent Refer Object CustomShapes ;
end Object


# ----------------------------- MESH --------------------- # 

Mesh GZM_Hook GZM_Hook 
  Verts
    v 0.000 0.650 0.000 ;
    v 0.000 0.350 0.000 ;
    v 0.000 0.446 0.384 ;
    v 0.000 0.554 0.384 ;
    v 0.000 0.650 0.038 ;
    v 0.000 0.350 0.038 ;
    v 0.000 0.000 0.000 ;
    v 0.000 0.000 0.038 ;
    v 0.000 1.000 0.000 ;
    v 0.000 1.000 0.038 ;
    v 0.000 0.650 0.155 ;
    v 0.000 0.350 0.155 ;
  end Verts
  Faces
    f 0 4 5 1 ;
    f 1 5 7 6 ;
    f 4 0 8 9 ;
    f 4 10 11 5 ;
    f 10 3 2 11 ;
    ftall 0 0 ;
  end Faces
end Mesh

Object GZM_Hook MESH GZM_Hook
  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;
  parent Refer Object CustomShapes ;
end Object

""")
