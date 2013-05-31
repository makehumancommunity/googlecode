


    Video: 39827744, "Video::texture_png", "Clip" {
        Type: "Clip"
        Properties70:  {
            P: "Path", "KString", "XRefUrl", "", "C:\Users\Simulering\Documents\makehuman\exports\textures\texture.png"
        }
        UseMipMap: 0
        Filename: "C:\Users\Simulering\Documents\makehuman\exports\textures\texture.png"
        RelativeFilename: "textures\texture.png"
    }
    Texture: 39534816, "Texture::texture_png", "" {
        Type: "TextureVideoClip"
        Version: 202
        TextureName: "Texture::texture_png"
        Properties70:  {
            P: "COLLADA_ID", "KString", "", "", "texture_png"
        }
        Media: "Video::texture_png"
        FileName: "C:\Users\Simulering\Documents\makehuman\exports\textures\texture.png"
        RelativeFilename: "textures\texture.png"
        ModelUVTranslation: 0,0
        ModelUVScaling: 1,1
        Texture_Alpha_Source: "None"
        Cropping: 0,0,0,0
    }
    AnimationStack: 39483280, "AnimStack::Take 001", "" {
    }
    AnimationLayer: 39462176, "AnimLayer::Layer0", "" {
    }
    CollectionExclusive: 39363008, "DisplayLayer::L1", "DisplayLayer" {
    }
}

; Object connections
;------------------------------------------------------------------

Connections:  {
    
    ;Model::foo, Model::RootNode
    C: "OO",39462608,0
    
    ;AnimLayer::Layer0, AnimStack::Take 001
    C: "OO",39462176,39483280
    
    ;Model::Hips, Model::foo
    C: "OO",39477920,39462608
    
    ;Model::foo, Model::foo
    C: "OO",40892128,39462608
    
    ;Model::Hips, DisplayLayer::L1
    C: "OO",39477920,39363008
    
    ;Model::UpLeg_L, Model::Hips
    C: "OO",39480176,39477920
    
    ;Model::Spine1, Model::Hips
    C: "OO",39912240,39477920
    
    ;Model::UpLeg_R, Model::Hips
    C: "OO",40882848,39477920
    
    ;NodeAttribute::Hips, Model::Hips
    C: "OO",40993472,39477920
    
    ;Model::LoLeg_L, Model::UpLeg_L
    C: "OO",39531536,39480176
    
    ;NodeAttribute::UpLeg_L, Model::UpLeg_L
    C: "OO",39364416,39480176
    
    ;Model::Foot_L, Model::LoLeg_L
    C: "OO",39866768,39531536
    
    ;NodeAttribute::LoLeg_L, Model::LoLeg_L
    C: "OO",39364064,39531536
    
    ;Model::Toe_L, Model::Foot_L
    C: "OO",39877216,39866768
    
    ;NodeAttribute::Foot_L, Model::Foot_L
    C: "OO",39363712,39866768
    
    ;NodeAttribute::Toe_L, Model::Toe_L
    C: "OO",39363360,39877216
    
    ;Model::Spine2, Model::Spine1
    C: "OO",39914496,39912240
    
    ;NodeAttribute::Spine1, Model::Spine1
    C: "OO",40991712,39912240
    
    ;Model::Neck, Model::Spine2
    C: "OO",39924944,39914496
    
    ;Model::Clavicle_L, Model::Spine2
    C: "OO",40845728,39914496
    
    ;Model::Clavicle_R, Model::Spine2
    C: "OO",40864288,39914496
    
    ;NodeAttribute::Spine2, Model::Spine2
    C: "OO",40991360,39914496
    
    ;Model::Head, Model::Neck
    C: "OO",40841088,39924944
    
    ;NodeAttribute::Neck, Model::Neck
    C: "OO",39365472,39924944
    
    ;Model::Jaw, Model::Head
    C: "OO",40843408,40841088
    
    ;NodeAttribute::Head, Model::Head
    C: "OO",39365120,40841088
    
    ;NodeAttribute::Jaw, Model::Jaw
    C: "OO",39364768,40843408
    
    ;Model::UpArm_L, Model::Clavicle_L
    C: "OO",40848048,40845728
    
    ;NodeAttribute::Clavicle_L, Model::Clavicle_L
    C: "OO",39368288,40845728
    
    ;Model::LoArm_L, Model::UpArm_L
    C: "OO",40850368,40848048
    
    ;NodeAttribute::UpArm_L, Model::UpArm_L
    C: "OO",39367936,40848048
    
    ;Model::Hand_L, Model::LoArm_L
    C: "OO",40852688,40850368
    
    ;NodeAttribute::LoArm_L, Model::LoArm_L
    C: "OO",39367584,40850368
    
    ;Model::Mit_L, Model::Hand_L
    C: "OO",40855008,40852688
    
    ;Model::Thumb1_L, Model::Hand_L
    C: "OO",40857328,40852688
    
    ;Model::Index_L, Model::Hand_L
    C: "OO",40861968,40852688
    
    ;NodeAttribute::Hand_L, Model::Hand_L
    C: "OO",39367232,40852688
    
    ;NodeAttribute::Mit_L, Model::Mit_L
    C: "OO",39365824,40855008
    
    ;Model::Thumb2_L, Model::Thumb1_L
    C: "OO",40859648,40857328
    
    ;NodeAttribute::Thumb1_L, Model::Thumb1_L
    C: "OO",39366528,40857328
    
    ;NodeAttribute::Thumb2_L, Model::Thumb2_L
    C: "OO",39366176,40859648
    
    ;NodeAttribute::Index_L, Model::Index_L
    C: "OO",39366880,40861968
    
    ;Model::UpArm_R, Model::Clavicle_R
    C: "OO",40866608,40864288
    
    ;NodeAttribute::Clavicle_R, Model::Clavicle_R
    C: "OO",40991008,40864288
    
    ;Model::LoArm_R, Model::UpArm_R
    C: "OO",40868928,40866608
    
    ;NodeAttribute::UpArm_R, Model::UpArm_R
    C: "OO",40990656,40866608
    
    ;Model::Hand_R, Model::LoArm_R
    C: "OO",40871248,40868928
    
    ;NodeAttribute::LoArm_R, Model::LoArm_R
    C: "OO",40990304,40868928
    
    ;Model::Mit_R, Model::Hand_R
    C: "OO",40873568,40871248
    
    ;Model::Index_R, Model::Hand_R
    C: "OO",40875888,40871248
    
    ;Model::Thumb1_R, Model::Hand_R
    C: "OO",40878208,40871248
    
    ;NodeAttribute::Hand_R, Model::Hand_R
    C: "OO",40989952,40871248
    
    ;NodeAttribute::Mit_R, Model::Mit_R
    C: "OO",40988544,40873568
    
    ;NodeAttribute::Index_R, Model::Index_R
    C: "OO",40988896,40875888
    
    ;Model::Thumb2_R, Model::Thumb1_R
    C: "OO",40880528,40878208
    
    ;NodeAttribute::Thumb1_R, Model::Thumb1_R
    C: "OO",40989600,40878208
    
    ;NodeAttribute::Thumb2_R, Model::Thumb2_R
    C: "OO",40989248,40880528
    
    ;Model::LoLeg_R, Model::UpLeg_R
    C: "OO",40885168,40882848
    
    ;NodeAttribute::UpLeg_R, Model::UpLeg_R
    C: "OO",40993120,40882848
    
    ;Model::Foot_R, Model::LoLeg_R
    C: "OO",40887488,40885168
    
    ;NodeAttribute::LoLeg_R, Model::LoLeg_R
    C: "OO",40992768,40885168
    
    ;Model::Toe_R, Model::Foot_R
    C: "OO",40889808,40887488
    
    ;NodeAttribute::Foot_R, Model::Foot_R
    C: "OO",40992416,40887488
    
    ;NodeAttribute::Toe_R, Model::Toe_R
    C: "OO",40992064,40889808
    
    ;Material::SkinShader, Model::foo
    C: "OO",39482432,40892128
    
    ;Geometry::foo, Model::foo
    C: "OO",39953856,40892128
    
    ;Texture::texture_png, Material::SkinShader
    C: "OP",39534816,39482432, "DiffuseColor"
    
    ;Texture::texture_png, Material::SkinShader
    C: "OP",39534816,39482432, "TransparentColor"
    
    ;Video::texture_png, Texture::texture_png
    C: "OO",39827744,39534816
    
    ;Deformer::foo-skin, Geometry::foo
    C: "OO",39954544,39953856
    
    ;SubDeformer::Hips, Deformer::foo-skin
    C: "OO",47254192,39954544
    
    ;SubDeformer::UpLeg_L, Deformer::foo-skin
    C: "OO",47259424,39954544
    
    ;SubDeformer::LoLeg_L, Deformer::foo-skin
    C: "OO",47260560,39954544
    
    ;SubDeformer::Foot_L, Deformer::foo-skin
    C: "OO",47261696,39954544
    
    ;SubDeformer::Toe_L, Deformer::foo-skin
    C: "OO",47262832,39954544
    
    ;SubDeformer::Spine1, Deformer::foo-skin
    C: "OO",47263968,39954544
    
    ;SubDeformer::Spine2, Deformer::foo-skin
    C: "OO",47265104,39954544
    
    ;SubDeformer::Neck, Deformer::foo-skin
    C: "OO",47266240,39954544
    
    ;SubDeformer::Head, Deformer::foo-skin
    C: "OO",45665056,39954544
    
    ;SubDeformer::Jaw, Deformer::foo-skin
    C: "OO",45666192,39954544
    
    ;SubDeformer::Clavicle_L, Deformer::foo-skin
    C: "OO",45667328,39954544
    
    ;SubDeformer::UpArm_L, Deformer::foo-skin
    C: "OO",45668464,39954544
    
    ;SubDeformer::LoArm_L, Deformer::foo-skin
    C: "OO",45669600,39954544
    
    ;SubDeformer::Hand_L, Deformer::foo-skin
    C: "OO",45674832,39954544
    
    ;SubDeformer::Mit_L, Deformer::foo-skin
    C: "OO",41328480,39954544
    
    ;SubDeformer::Thumb1_L, Deformer::foo-skin
    C: "OO",41329616,39954544
    
    ;SubDeformer::Thumb2_L, Deformer::foo-skin
    C: "OO",41339968,39954544
    
    ;SubDeformer::Index_L, Deformer::foo-skin
    C: "OO",41341152,39954544
    
    ;SubDeformer::Clavicle_R, Deformer::foo-skin
    C: "OO",41342320,39954544
    
    ;SubDeformer::UpArm_R, Deformer::foo-skin
    C: "OO",41343488,39954544
    
    ;SubDeformer::LoArm_R, Deformer::foo-skin
    C: "OO",41344656,39954544
    
    ;SubDeformer::Hand_R, Deformer::foo-skin
    C: "OO",41345824,39954544
    
    ;SubDeformer::Mit_R, Deformer::foo-skin
    C: "OO",41346992,39954544
    
    ;SubDeformer::Index_R, Deformer::foo-skin
    C: "OO",41348160,39954544
    
    ;SubDeformer::Thumb1_R, Deformer::foo-skin
    C: "OO",41349328,39954544
    
    ;SubDeformer::Thumb2_R, Deformer::foo-skin
    C: "OO",41350496,39954544
    
    ;SubDeformer::UpLeg_R, Deformer::foo-skin
    C: "OO",41351664,39954544
    
    ;SubDeformer::LoLeg_R, Deformer::foo-skin
    C: "OO",41352832,39954544
    
    ;SubDeformer::Foot_R, Deformer::foo-skin
    C: "OO",41354000,39954544
    
    ;SubDeformer::Toe_R, Deformer::foo-skin
    C: "OO",41355168,39954544
    
    ;Model::Hips, SubDeformer::Hips
    C: "OO",39477920,47254192
    
    ;Model::UpLeg_L, SubDeformer::UpLeg_L
    C: "OO",39480176,47259424
    
    ;Model::LoLeg_L, SubDeformer::LoLeg_L
    C: "OO",39531536,47260560
    
    ;Model::Foot_L, SubDeformer::Foot_L
    C: "OO",39866768,47261696
    
    ;Model::Toe_L, SubDeformer::Toe_L
    C: "OO",39877216,47262832
    
    ;Model::Spine1, SubDeformer::Spine1
    C: "OO",39912240,47263968
    
    ;Model::Spine2, SubDeformer::Spine2
    C: "OO",39914496,47265104
    
    ;Model::Neck, SubDeformer::Neck
    C: "OO",39924944,47266240
    
    ;Model::Head, SubDeformer::Head
    C: "OO",40841088,45665056
    
    ;Model::Jaw, SubDeformer::Jaw
    C: "OO",40843408,45666192
    
    ;Model::Clavicle_L, SubDeformer::Clavicle_L
    C: "OO",40845728,45667328
    
    ;Model::UpArm_L, SubDeformer::UpArm_L
    C: "OO",40848048,45668464
    
    ;Model::LoArm_L, SubDeformer::LoArm_L
    C: "OO",40850368,45669600
    
    ;Model::Hand_L, SubDeformer::Hand_L
    C: "OO",40852688,45674832
    
    ;Model::Mit_L, SubDeformer::Mit_L
    C: "OO",40855008,41328480
    
    ;Model::Thumb1_L, SubDeformer::Thumb1_L
    C: "OO",40857328,41329616
    
    ;Model::Thumb2_L, SubDeformer::Thumb2_L
    C: "OO",40859648,41339968
    
    ;Model::Index_L, SubDeformer::Index_L
    C: "OO",40861968,41341152
    
    ;Model::Clavicle_R, SubDeformer::Clavicle_R
    C: "OO",40864288,41342320
    
    ;Model::UpArm_R, SubDeformer::UpArm_R
    C: "OO",40866608,41343488
    
    ;Model::LoArm_R, SubDeformer::LoArm_R
    C: "OO",40868928,41344656
    
    ;Model::Hand_R, SubDeformer::Hand_R
    C: "OO",40871248,41345824
    
    ;Model::Mit_R, SubDeformer::Mit_R
    C: "OO",40873568,41346992
    
    ;Model::Index_R, SubDeformer::Index_R
    C: "OO",40875888,41348160
    
    ;Model::Thumb1_R, SubDeformer::Thumb1_R
    C: "OO",40878208,41349328
    
    ;Model::Thumb2_R, SubDeformer::Thumb2_R
    C: "OO",40880528,41350496
    
    ;Model::UpLeg_R, SubDeformer::UpLeg_R
    C: "OO",40882848,41351664
    
    ;Model::LoLeg_R, SubDeformer::LoLeg_R
    C: "OO",40885168,41352832
    
    ;Model::Foot_R, SubDeformer::Foot_R
    C: "OO",40887488,41354000
    
    ;Model::Toe_R, SubDeformer::Toe_R
    C: "OO",40889808,41355168
}
;Takes section
;----------------------------------------------------

Takes:  {
    Current: ""
    Take: "Take 001" {
        FileName: "Take_001.tak"
        LocalTime: 0,46186158000
        ReferenceTime: 0,46186158000
    }
}
