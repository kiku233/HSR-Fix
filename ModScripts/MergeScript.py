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
import time

from NarakaMergeUtil import *
import logging
import time
import configparser


def get_pointlit_and_trianglelist_indices_V2():
    draw_ib = preset_config["Merge"]["draw_ib"]
    root_vs = preset_config["Merge"]["root_vs"]
    use_pointlist = preset_config["Merge"]["use_pointlist"]

    logging.info("执行函数：get_pointlit_and_trianglelist_indices_V2(HSR)")
    logging.info("开始读取所有vb0文件的index列表：")

    indices = get_filter_vb_indices(WorkFolder,"-vb0")

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    """
    format:
    {index:vertex count,index2,vertex count2,...}
    """

    trianglelist_vertex_count = b"0"

    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):

        vb0_filename = get_filter_filenames(WorkFolder,indices[index] + "-vb0",".txt")[0]

        logging.info("当前处理的vb0文件：" + vb0_filename)
        topology, vertex_count = get_topology_vertexcount(WorkFolder + vb0_filename)
        logging.info("当前vb0文件的topology：" + str(topology))
        logging.info("当前vb0文件的vertex_count：" + str(vertex_count))

        if topology == b"pointlist":
            # print("index: " + str(indices[index]) + " VertexCount = " + str(vertex_count))

            # Filter, vb0 filename must have ROOT VS.
            if use_pointlist:
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count

        ib_filename = get_filter_filenames(WorkFolder,indices[index] + "-ib", ".txt")[0]
        logging.info("当前处理的ib文件：" + ib_filename)

        topology, vertex_count = get_topology_vertexcount(WorkFolder + ib_filename)
        logging.info("当前ib文件的topology： "+str(topology))
        logging.info("当前ib文件的vertex_count： "+str(vertex_count))
        logging.info(split_str)

        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            if draw_ib in ib_filename:
                topology, vertex_count = get_topology_vertexcount(WorkFolder + vb0_filename)
                trianglelist_indices_dict[(indices[index])] = vertex_count

                """
                在所有的游戏中，即使一个index buffer中出现了多个index的多个vertex count,
                只有最大的那个vertex count是整个index buffer的
                """
                vertex_count_int = int.from_bytes(vertex_count, "big")
                trianglelist_vertex_count_int = int.from_bytes(trianglelist_vertex_count, "big")

                logging.info("vertex_count_int:")
                logging.info(vertex_count_int)
                logging.info("trianglelist_vertex_count_int:")
                logging.info(trianglelist_vertex_count_int)

                if  vertex_count_int >= trianglelist_vertex_count_int:
                    trianglelist_vertex_count = vertex_count
                    logging.info(trianglelist_vertex_count)

    logging.info("Based on vertex count, remove the duplicated pointlist indices.")
    logging.info("output pointlist and trianglelist before remove:")
    logging.info(pointlist_indices_dict)
    logging.info(trianglelist_indices_dict)

    # 输出一下vertex_count，看看是否正常
    logging.info(trianglelist_vertex_count)

    # 注意，星穹铁道中相同的pointlist会出现两次，且数值完全一样
    pointlist_indices = []
    trianglelist_indices = []
    for pointlist_index in pointlist_indices_dict:
        if pointlist_indices_dict.get(pointlist_index) == trianglelist_vertex_count:
            pointlist_indices.append(pointlist_index)

    for trianglelist_index in trianglelist_indices_dict:
        trianglelist_indices.append(trianglelist_index)

    logging.info("indices全部处理完毕")
    logging.info("----------------------------------------------------------")
    logging.info("Pointlist vb indices: " + str(pointlist_indices))
    logging.info("Trianglelist vb indices: " + str(trianglelist_indices))
    logging.info("函数：get_pointlit_and_trianglelist_indices_v2执行完成")

    return pointlist_indices, trianglelist_indices


def save_output_ini_body(pointlist_indices, merge_info=MergeInfo()):
    # don't care if pointlist_indices has many candidates,because we only use one of them
    # because they are totally same,just show twice in pointlist files.
    filenames = sorted(get_filter_filenames(WorkFolder,pointlist_indices[0] + "-vb",".txt"))

    tmp_config = configparser.ConfigParser()
    tmp_config.read('configs/tmp.ini')

    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]

    blend_vb = filenames[2]
    blend_vb = blend_vb[blend_vb.find("-vb2=") + 5:blend_vb.find("-vs=")]

    tmp_config.set("Ini", "position_vb", position_vb)
    tmp_config.set("Ini", "texcoord_vb", texcoord_vb)
    tmp_config.set("Ini", "blend_vb", blend_vb)

    vertex_config = configparser.ConfigParser()
    vertex_config.read('configs/vertex_attr_body.ini')

    element_list = merge_info.info_location.keys()

    position_stride = 0
    texcoord_stride = 0
    blend_stride = 0

    for element in element_list:
        byte_width = vertex_config[element.decode()].getint("byte_width")
        print(byte_width)
        print("---------")
        if merge_info.info_location.get(element) == "vb0":
            position_stride = position_stride + byte_width
        if merge_info.info_location.get(element) == "vb1":
            texcoord_stride = texcoord_stride + byte_width
        if merge_info.info_location.get(element) == "vb2":
            blend_stride = blend_stride + byte_width

    tmp_config.set("Ini", "position_stride", str(position_stride))
    tmp_config.set("Ini", "texcoord_stride", str(texcoord_stride))
    tmp_config.set("Ini", "blend_stride", str(blend_stride))


    # 保存
    tmp_config.write(open("configs/tmp.ini","w"))


def output_action_ini_file(pointlist_indices, input_ib_hash, part_name, match_first_index):
    # don't care if pointlist_indices has many candidates,because we only use one of them
    # because they are totally same,just show twice in pointlist files.

    logging.info(split_str)
    logging.info("Start to generate "+part_name+"'s ini config file.")

    filenames = sorted(get_filter_filenames(WorkFolder,pointlist_indices[0] + "-vb",".txt"))
    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]
    logging.info("position_vb: " + str(position_vb))

    # In HSR we cannot find the correct texcoord hash,so we use it in index buffer hash.

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]
    logging.info("texcoord_vb: " + str(texcoord_vb))

    blend_vb = filenames[2]
    blend_vb = blend_vb[blend_vb.find("-vb2=") + 5:blend_vb.find("-vs=")]
    logging.info("blend_vb: " + str(blend_vb))

    output_bytes = b""
    output_bytes = output_bytes + (b"[Resource_POSITION]\r\ntype = Buffer\r\nstride = 40\r\nfilename = " + part_name.encode() + b"_POSITION.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_BLEND]\r\ntype = Buffer\r\nstride = 32\r\nfilename = " + part_name.encode() + b"_BLEND.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_TEXCOORD]\r\ntype = Buffer\r\nstride = 20\r\nfilename = " + part_name.encode() + b"_TEXCOORD.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_IB_FILE]\r\ntype = Buffer\r\nformat = DXGI_FORMAT_R16_UINT\r\nfilename = " + part_name.encode() + b".ib\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_"+part_name.encode() + b"]\r\nfilename = "+ part_name.encode()+b".png\r\n\r\n")

    output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nhandling = skip\r\nmatch_first_index = "+ match_first_index +b"\r\nib = Resource_IB_FILE\r\n;ps-t0 = Resource_"+ part_name.encode()+b"\r\ndrawindexed = auto\r\n\r\n")
    # output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nmatch_first_index = "+ match_first_index +b"\r\nhandling = skip\r\nib = Resource_IB_FILE\r\n;ps-t0 = Resource_"+ part_name.encode()+b"\r\ndrawindexed = auto\r\n\r\n")

    # In HSR,we need a vb3 to fix the outline problem.
    # Normally we don't need a vb3,but maybe sometime it need.
    output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\n\r\n")
    # output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\nvb3 = Resource_POSITION\r\n\r\n")

    # TODO drawindexed cannot work perfectly! need to use draw xxx,0  xxx is calculated in GIMI's blender script.
    #  we now can make sure that this xxx value is comes from
    #  (the length of position file's bytes / the stride of position file)
    #  Even with the right draw number,the texcoord still cannot draw in the texcoord hash correctly,but GIMI can do this correctly.
    #  very strange,but now we can only use the IB to replace vb1 texcoord.
    # output_bytes = output_bytes + (b"[TextureOverride_TEXCOORD]\r\nhash = "+texcoord_vb.encode()+b"\r\nvb1 = Resource_TEXCOORD\r\nhandling = skip\r\ndrawindexed = auto\r\n;draw = xxx,0\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_TEXCOORD]\r\n;hash = "+texcoord_vb.encode()+b"\r\n;vb1 = Resource_TEXCOORD\r\n;handling = skip\r\n;drawindexed = auto\r\n;draw = xxx,0\r\n\r\n")

    output_bytes = output_bytes + (b"[TextureOverride_BLEND]\r\nhash = "+blend_vb.encode()+b"\r\nvb2 = Resource_BLEND\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_VB_SKIP_Other_1]\r\n;hash = \r\n;handling = skip\r\n\r\n")

    logging.info(part_name + "  generated file content is: ")
    logging.info(str(output_bytes))

    output_file = open(preset_config["General"]["OutputFolder"] + part_name+".ini", "wb+")
    output_file.write(output_bytes)
    output_file.close()
    logging.info("Generate "+part_name+"'s ini config file completed.")



def output_trianglelist_ini_file(pointlist_indices, input_ib_hash, part_name):

    print("Start to output ini file.")
    filenames = sorted(glob.glob(pointlist_indices[0] + '-vb*txt'))
    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]

    print("position_vb: " + position_vb)
    print("texcoord_vb: " + texcoord_vb)

    output_bytes = b""
    output_bytes = output_bytes + (b"[Resource_POSITION]\r\ntype = Buffer\r\nstride = 40\r\nfilename = " + part_name.encode() + b"_POSITION.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_TEXCOORD]\r\ntype = Buffer\r\nstride = 8\r\nfilename = " + part_name.encode() + b"_TEXCOORD.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_IB_FILE]\r\ntype = Buffer\r\nformat = DXGI_FORMAT_R16_UINT\r\nfilename = " + part_name.encode() + b".ib\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_"+part_name.encode() + b"]\r\nfilename = "+ part_name.encode()+b".png\r\n\r\n")

    output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nhandling = skip\r\nib = Resource_IB_FILE\r\n;ps-t7 = Resource_"+ part_name.encode()+b"\r\ndrawindexed = auto\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_TEXCOORD]\r\nhash = "+texcoord_vb.encode()+b"\r\nvb1 = Resource_TEXCOORD\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_VB_SKIP_1]\r\n;hash = \r\n;handling = skip\r\n\r\n")

    output_file = open("output/"+part_name+".ini", "wb+")
    output_file.write(output_bytes)
    output_file.close()


def merge_pointlist_files(pointlist_indices, trianglelist_indices, merge_info=MergeInfo()):
    part_name = preset_config["Merge"]["part_name"]
    read_pointlist_element_list = merge_info.info_location.keys()

    logging.info("Start to move ps-t0 files to output folder.")
    move_related_files(trianglelist_indices, preset_config["General"]["OutputFolder"], move_dds=True, only_pst7=True)
    logging.info(split_str)

    logging.info("Start to read info from pointlist vb files(Only from pointlist files).")
    logging.info("The elements need to read is: " + str(read_pointlist_element_list))
    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0],
                                                                              merge_info)
    logging.info("Based on output_element_list，generate a final header_info.")

    header_info = get_header_info_by_elementnames(read_pointlist_element_list, merge_info.type)
    # Set vertex count
    header_info.vertex_count = str(len(pointlist_vertex_data_chunk_list)).encode()

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[
            index]

    logging.info("Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.")

    # Get element_aligned_byte_offsets to a new format.
    # Before set the output header info ,we need to fix the semantic name equals TEXCOORD1 problem
    # This will cause vb0 file can not import into blender.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        logging.info("-----------------")
        logging.info(element.semantic_name)
        logging.info(element.semantic_index)
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset

        # Fix texcoord1 problem
        if element.semantic_name.startswith(b"TEXCOORD") and element.semantic_index != b"0":
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    logging.info("Change aligned byte offset in vertex data")
    new_final_vertex_data_chunk_list = []
    for vertex_data_chunk in final_vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            vertex_data.aligned_byte_offset = element_aligned_byte_offsets[vertex_data.element_name]
            new_vertex_data_chunk.append(vertex_data)
        new_final_vertex_data_chunk_list.append(new_vertex_data_chunk)
    final_vertex_data_chunk_list = new_final_vertex_data_chunk_list

    output_vb_fileinfo = VbFileInfo()
    output_vb_fileinfo.header_info = header_info
    output_vb_fileinfo.vertex_data_chunk_list = final_vertex_data_chunk_list

    ib_file_bytes, ib_file_first_index_list = get_unique_ib_bytes_by_indices(trianglelist_indices)

    logging.info("Save ini information to tmp.ini")
    save_output_ini_body(pointlist_indices, merge_info)

    logging.info("Output to file.")
    for index in range(len(ib_file_bytes)):
        output_partname = part_name + "_part" + str(index)

        ib_file_byte = ib_file_bytes[index]
        output_vbname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + output_partname + "-vb0.txt"
        output_ibname = preset_config["General"]["OutputFolder"] + merge_info.draw_ib + "-" + output_partname + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        logging.info("Output Step 1: Write to ib file.")
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        logging.info("Output Step 2: Write to vb file.")
        output_vb_file(output_vb_fileinfo)

        logging.info("Output Step 3: Generate ini config file: ")
        if merge_info.type == "weapon":
            # TODO need to test with weapon export
            pass
        else:
            output_action_ini_file(pointlist_indices, merge_info.draw_ib, output_partname, ib_file_first_index_list[index])
        logging.info(split_str)


def merge_trianglelist_files(trianglelist_indices, part_name):
    output_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"TEXCOORD"]

    move_related_files(trianglelist_indices, move_dds=True, only_pst7=True)

    # The vertex data you want to read from trianglelist vb file.
    read_trianglelist_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"TEXCOORD"]

    # Read all the trianglelist indices.
    final_trianglelist_vertex_data_chunk_list_list = []
    for trianglelist_index in trianglelist_indices:
        vertex_data_chunk_list_tmp = read_vertex_data_chunk_list_gracefully(trianglelist_index, read_trianglelist_element_list, only_vb1=False, sanity_check=True)
        final_trianglelist_vertex_data_chunk_list_list.append(vertex_data_chunk_list_tmp)

    # Final output index
    final_output_indices = []

    # Remove the invalid file content.
    repeat_vertex_data_chunk_list_list = []
    count = 0
    for final_trianglelist_vertex_data_chunk_list in final_trianglelist_vertex_data_chunk_list_list:
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]

        # First,check if there have TEXCOORD, continue if not exists.
        element_name_list = []
        found_invalid_texcoord = False
        for vertex_data in first_vertex_data_chunk:
            element_name_list.append(vertex_data.element_name)
            datas = str(vertex_data.data.decode()).split(",")
            # Here > 2, because TEXCOORD's format must be R32G32_FLOAT.
            if vertex_data.element_name.startswith(b"TEXCOORD") and len(datas) > 2:
                found_invalid_texcoord = True
        if found_invalid_texcoord:
            continue

        # Must have at least one TEXCOORD
        if b"TEXCOORD" not in element_name_list:
            continue

        # for vertex_data in first_vertex_data_chunk:
        #     print(vertex_data.element_name)
        #     print(vertex_data.data)
        # print("-----------------------------------")

        repeat_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)
        final_output_indices.append(trianglelist_indices[count])
        count = count + 1

    # print(final_output_indices)

    new_final_output_indices = []
    count = 0

    # Remove duplicated contents.
    final_trianglelist_vertex_data_chunk_list_list = []
    repeat_check = []
    for final_trianglelist_vertex_data_chunk_list in repeat_vertex_data_chunk_list_list:
        # Grab the first one to check.
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        first_vertex_data = first_vertex_data_chunk[0]
        # 校验元素个数，必须和指定要输出的元素列表的元素个数相同
        if len(first_vertex_data_chunk) != len(output_element_list):
            count = count + 1
            continue

        if first_vertex_data.data not in repeat_check:
            repeat_check.append(first_vertex_data.data)
            final_trianglelist_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)
            new_final_output_indices.append(final_output_indices[count])
            count = count + 1

    print(new_final_output_indices)
    if len(final_trianglelist_vertex_data_chunk_list_list) != 1:
        print("The length after duplicate removal should be 1!")
        exit(1)

    # After duplicate removal, there should only be one element in list,so we use index [0].
    final_trianglelist_vertex_data_chunk_list = final_trianglelist_vertex_data_chunk_list_list[0]

    # Based on output_element_list，generate a final header_info.
    header_info = get_header_info_by_elementnames(output_element_list)
    # Set vertex count
    header_info.vertex_count = str(len(final_trianglelist_vertex_data_chunk_list)).encode()

    # Generate a final vb file.
    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(final_trianglelist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + final_trianglelist_vertex_data_chunk_list[index]

    # Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset
        if element.semantic_name.endswith(b"TEXCOORD1"):
            element.semantic_name = b"TEXCOORD"
        new_element_list.append(element)
    header_info.elementlist = new_element_list

    # Revise aligned byte offset
    new_final_vertex_data_chunk_list = []
    for vertex_data_chunk in final_vertex_data_chunk_list:
        new_vertex_data_chunk = []
        for vertex_data in vertex_data_chunk:
            vertex_data.aligned_byte_offset = element_aligned_byte_offsets[vertex_data.element_name]
            new_vertex_data_chunk.append(vertex_data)
        new_final_vertex_data_chunk_list.append(new_vertex_data_chunk)
    final_vertex_data_chunk_list = new_final_vertex_data_chunk_list

    output_vb_fileinfo = VbFileInfo()
    output_vb_fileinfo.header_info = header_info
    output_vb_fileinfo.vertex_data_chunk_list = final_vertex_data_chunk_list

    ib_file_bytes = get_unique_ib_bytes_by_indices(trianglelist_indices)

    # Output to file.
    for index in range(len(ib_file_bytes)):
        ib_file_byte = ib_file_bytes[index]
        output_vbname = "output/" + merge_info.draw_ib + "-" + part_name + "-vb0.txt"
        output_ibname = "output/" + merge_info.draw_ib + "-" + part_name + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        # Write to ib file.
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        # Write to vb file.
        output_vb_file(output_vb_fileinfo)
        # Finally, output ini file.
    output_trianglelist_ini_file(final_output_indices, merge_info.draw_ib, part_name)



def start_merge_files(merge_info= MergeInfo()):
    logging.info("Start to read pointlist and trianglelist indices.")
    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices_V2()

    if use_pointlist_tech:
        if len(pointlist_indices) == 0:
            logging.error("Can't find any pointlist file,please turn pointlist tech flag to False for:")
            logging.error("['" + preset_config["Merge"]["part_name"] + "']")
            exit(1)

        if merge_info.only_pointlist:
            merge_pointlist_files(pointlist_indices, trianglelist_indices, merge_info)
        else:
            # I see the texcoord info stored in pointlist and trianglelist is same.
            # But GIMI designed to collect TEXCOORD info from trianglelist.
            # I still think collect from pointlist will be neat and nice.
            pass
    else:
        # TODO need to fix this method,it can not work now.
        logging.info("Only fetch from trianglelist files.")
        merge_trianglelist_files(trianglelist_indices, preset_config["Merge"]["part_name"])


if __name__ == "__main__":
    preset_config = configparser.ConfigParser()
    preset_config.read('configs/preset.ini')
    split_str = "----------------------------------------------------------------------------------------------"

    # General Info
    GameName = preset_config["General"]["GameName"]
    OutputFolder = preset_config["General"]["OutputFolder"]
    LoaderFolder = preset_config["General"]["LoaderFolder"]
    FrameAnalyseFolder = preset_config["General"]["FrameAnalyseFolder"]
    WorkFolder = LoaderFolder + FrameAnalyseFolder + "/"

    # Merge Info
    merge_info = MergeInfo()
    merge_info.part_name = preset_config["Merge"]["part_name"]
    merge_info.type = preset_config["Merge"]["type"]
    merge_info.root_vs = preset_config["Merge"]["root_vs"]
    merge_info.draw_ib = preset_config["Merge"]["draw_ib"]
    merge_info.use_pointlist = preset_config["Merge"].getboolean("use_pointlist")
    merge_info.only_pointlist = preset_config["Merge"].getboolean("only_pointlist")

    # Automatically get element list and which vb file it's extracted from by read config file.
    vertex_config = configparser.ConfigParser()
    if preset_config["Merge"]["type"] == "weapon":
        vertex_config.read('configs/vertex_attr_weapon.ini')
    else:
        vertex_config.read('configs/vertex_attr_body.ini')
    element_list = preset_config["Merge"]["element_list"].split(",")
    info_location = {}
    for element in element_list:
        extract_vb_file = vertex_config[element]["extract_vb_file"]
        info_location[element.encode()] = extract_vb_file
    merge_info.info_location = info_location

    # Decide weather to create a new one.
    DeleteOutputFolder = preset_config["General"].getboolean("DeleteOutputFolder")
    if DeleteOutputFolder:
        shutil.rmtree(OutputFolder)
    # Make sure the OutputFolder exists.
    if not os.path.exists(OutputFolder):
        os.mkdir(OutputFolder)

    # set the output log file.
    logging.basicConfig(filename=OutputFolder + str(time.strftime('%Y-%m-%d_%H_%M_%S_')) + str(time.time_ns()) + '.log', level=logging.DEBUG)

    logging.info("HSR MergeScript Current Version V0.1")
    logging.info("Switch to work dir: " + WorkFolder)
    logging.info(split_str)

    logging.info("Current Game: " + GameName)
    logging.info("Set RootVS To: " + merge_info.root_vs)
    logging.info("Set LoaderFolder To:" + LoaderFolder)
    logging.info("Set FrameAnalyseFolder To: " + FrameAnalyseFolder)
    logging.info("Set work dir to: " + WorkFolder)
    logging.info(split_str)

    logging.info("Start to process hash: " + merge_info.draw_ib)
    logging.info("Current hash's part name: " + merge_info.part_name)

    use_pointlist_tech = merge_info.use_pointlist
    logging.info("Whether current object use Pointlist Topology: " + str(use_pointlist_tech))

    start_merge_files(merge_info)
    logging.info(split_str)

    logging.info("----------------------------------------------------------\r\nAll process done！")
