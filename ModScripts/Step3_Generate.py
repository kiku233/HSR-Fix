"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os
import configparser


if __name__ == "__main__":
    # for convenience,the format we generate will as same as GIMI output format.
    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')

    preset_config = configparser.ConfigParser()
    preset_config.read('configs/preset.ini')
    LoaderFolder = preset_config["General"]["LoaderFolder"]

    mod_name = preset_config["General"]["mod_name"]
    mod_folder = LoaderFolder + "output/"
    mod_ini_name = mod_folder + mod_name +".ini"
    # -----------------------------------------------------------------------------------------------------------


    output_str = ""
    output_str = output_str + "; " + mod_name + "\n" + "\n"

    split_str = "-------------------------"
    output_str = output_str + "; Constants " + split_str + "\n" + "\n"
    output_str = output_str + "; Overrides " + split_str + "\n" + "\n"

    resource_position_name = "Resource_" + mod_name + "_POSITION"
    position_vb = tmp_config["Ini"]["position_vb"]
    output_str = output_str + "[TextureOverride_" + mod_name + "_POSITION]" + "\n"
    output_str = output_str + "hash = " + position_vb + "\n"
    output_str = output_str + "vb0 = " + resource_position_name + "\n" + "\n"

    resource_blend_name = "Resource_" + mod_name + "_BLEND"
    blend_vb = tmp_config["Ini"]["blend_vb"]
    output_str = output_str + "[TextureOverride_" + mod_name + "_BLEND]" + "\n"
    output_str = output_str + "hash = " + blend_vb + "\n"
    output_str = output_str + "vb2 = " + resource_blend_name + "\n" + "\n"

    resource_texcoord_name = "Resource_" + mod_name + "_TEXCOORD"
    texcoord_vb = tmp_config["Ini"]["texcoord_vb"]
    output_str = output_str + "[TextureOverride_" + mod_name + "_TEXCOORD]" + "\n"
    output_str = output_str + "hash = " + texcoord_vb + "\n"
    output_str = output_str + "vb1 = " + resource_texcoord_name + "\n" + "\n"

    # GIMI have a VertexLimitRaise,but original 3dmigoto don't have.
    output_str = output_str + "[TextureOverride_" + mod_name +"_VertexLimitRaise]" + "\n"
    draw_ib = preset_config["Merge"]["draw_ib"]
    output_str = output_str + "hash = " + draw_ib + "\n" + "\n"

    # -----------------------------------------------------------------------------------------------------------
    # TODO 这里要注意，如果ib里面只有一个,则有不同的生成逻辑
    part_names = tmp_config["Ini"]["part_names"].split(",")

    if len(part_names) == 1:
        output_str = output_str + "[TextureOverride_" + mod_name + "_IB]" + "\n"
        output_str = output_str + "hash = " + draw_ib + "\n"
        output_str = output_str + "handling = skip\n\n"

        match_first_index = tmp_config["Ini"]["match_first_index"].split(",")
        resource_ib_partnames = []
        for part_name in part_names:
            name = "Resource_" + mod_name + "_" + part_name
            resource_ib_partnames.append(name)

        for i in range(len(part_names)):
            part_name = part_names[i]
            first_index = match_first_index[i]
            output_str = output_str + "[TextureOverride_" + mod_name + "_" + part_name + "]\n"
            output_str = output_str + "hash = " + draw_ib + "\n"
            output_str = output_str + "match_first_index = " + first_index + "\n"
            output_str = output_str + "ib = " + resource_ib_partnames[i] + "\n"
            output_str = output_str + "vb1 = " + resource_texcoord_name + "\n"
            output_str = output_str + "drawindexed = auto\n\n"
    else:
        output_str = output_str + "[TextureOverride_" + mod_name + "_IB]" + "\n"
        output_str = output_str + "hash = " + draw_ib + "\n"
        output_str = output_str + "handling = skip\n"
        output_str = output_str + "drawindexed = auto\n\n"

        # TODO GIMI中把ib计算后分开了，但是vb是整体的分割,我们需要像GIMI那样分割ib
        #  先测试导出的时候分别导出ib，然后融合后导出一个整的vb是否管用

        match_first_index = tmp_config["Ini"]["match_first_index"].split(",")
        resource_ib_partnames = []
        for part_name in part_names:
            name = "Resource_" + mod_name + "_" + part_name
            resource_ib_partnames.append(name)

        for i in range(len(part_names)):
            part_name = part_names[i]
            first_index = match_first_index[i]
            output_str = output_str + "[TextureOverride_" + mod_name + "_" + part_name + "]\n"
            output_str = output_str + "hash = " + draw_ib + "\n"
            output_str = output_str + "match_first_index = " + first_index + "\n"
            output_str = output_str + "ib = " + resource_ib_partnames[i] + "\n"
            output_str = output_str + "vb1 = " + resource_texcoord_name + "\n" + "\n"


    # -----------------------------------------------------------------------------------------------------------
    output_str = output_str + "; CommandList " + split_str + "\n" + "\n"
    output_str = output_str + "; Resources " + split_str + "\n" + "\n"

    output_str = output_str + "[" + resource_position_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["position_stride"] + "\n"
    output_str = output_str + "filename = " + mod_name +"_POSITION.buf\n\n"

    output_str = output_str + "[" + resource_blend_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["blend_stride"] + "\n"
    output_str = output_str + "filename = " + mod_name +"_BLEND.buf\n\n"

    output_str = output_str + "[" + resource_texcoord_name + "]\n"
    output_str = output_str + "type = Buffer\n"
    output_str = output_str + "stride = " + tmp_config["Ini"]["texcoord_stride"] + "\n"
    output_str = output_str + "filename = " + mod_name +"_TEXCOORD.buf\n\n"

    for i in range(len(part_names)):
        part_name = part_names[i]
        resource_name = resource_ib_partnames[i]
        output_str = output_str + "[" + resource_name +"]\n"
        output_str = output_str + "type = Buffer\n"
        output_str = output_str + "format = " + preset_config["Merge"]["ib_format"] + "\n"
        output_str = output_str + "filename = " + mod_name + ".ib\n\n"

    # -----------------------------------------------------------------------------------------------------------
    output_str = output_str + "; .ini generated by HSR-Fix script.\n"
    output_str = output_str + "; Github: https://github.com/airdest/HSR-Fix"

    output_file = open(mod_ini_name, "w")
    output_file.write(output_str)
    output_file.close()



