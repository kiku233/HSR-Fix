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


def get_pointlit_and_trianglelist_indices_V2(input_ib_hash, root_vs, use_pointlist_tech):
    logging.info("执行函数：get_pointlit_and_trianglelist_indices_V2(HSR)")
    logging.info("开始读取所有vb0文件的index列表：")
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])
    logging.info(indices)

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    """
    format:
    {index:vertex count,index2,vertex count2,...}
    """

    trianglelist_vertex_count = b"0"

    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):
        vb0_filename = glob.glob(indices[index] + '-vb0*txt')[0]
        logging.info("当前处理的vb0文件：" + vb0_filename)
        topology, vertex_count = get_topology_vertexcount(vb0_filename)
        logging.info("当前vb0文件的topology：" + str(topology))
        logging.info("当前vb0文件的vertex_count：" + str(vertex_count))

        if topology == b"pointlist":
            # print("index: " + str(indices[index]) + " VertexCount = " + str(vertex_count))

            # Filter, vb0 filename must have ROOT VS.
            if use_pointlist_tech:
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count

        ib_filename = glob.glob(indices[index] + '-ib*txt')[0]
        logging.info("当前处理的ib文件：" + ib_filename)

        topology, vertex_count = get_topology_vertexcount(ib_filename)
        logging.info("当前ib文件的topology： "+str(topology))
        logging.info("当前ib文件的vertex_count： "+str(vertex_count))
        logging.info(split_str)

        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            if input_ib_hash in ib_filename:
                topology, vertex_count = get_topology_vertexcount(vb0_filename)
                trianglelist_indices_dict[(indices[index])] = vertex_count

                """
                在所有的游戏中，即使一个index buffer中出现了多个index的多个vertex count,
                只有最大的那个vertex count是整个index buffer的
                """
                if int.from_bytes(vertex_count,"little") >= int.from_bytes(trianglelist_vertex_count,"little"):
                    trianglelist_vertex_count = vertex_count
                    logging.info(trianglelist_vertex_count)



    logging.info("Based on vertex count, remove the duplicated pointlist indices.")
    logging.info("output pointlist and trianglelist before remove:")
    logging.info(pointlist_indices_dict)
    logging.info(trianglelist_indices_dict)

    # TODO 这里强行设置为前一个pointlist技术里有的，来测试一下输出的结果
    #  注意，这里trianglelist_vertex_count还是只有一个，且必须是所有draw中最大的哪一个
    # logging.info(trianglelist_vertex_count)
    # trianglelist_vertex_count = b"18389"

    pointlist_indices = []
    # TODO 注意，星穹铁道中相同的pointlist会出现两次，且数值完全一样


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



def get_pointlit_and_trianglelist_indices(input_ib_hash, root_vs, use_pointlist_tech):
    '''
    可以选择不使用pointlist_tech来导出武器、随人物衣服固定的物件等未装载到pointlist中的物件
    :param input_ib_hash:
    :param root_vs:
    :param use_pointlist_tech:
    :return:
    '''
    # The index number at the front of every file's filename.
    logging.info("执行函数：get_pointlit_and_trianglelist_indices")
    logging.info("开始读取所有vb0文件的index列表：")
    indices = sorted([re.findall('^\d+', x)[0] for x in glob.glob('*-vb0*txt')])
    logging.info(indices)

    pointlist_indices_dict = {}
    trianglelist_indices_dict = {}
    trianglelist_vertex_count = None
    # 1.First, grab all vb0 file's indices.
    for index in range(len(indices)):
        vb0_filename = glob.glob(indices[index] + '-vb0*txt')[0]
        logging.info("当前处理的vb0文件：" + vb0_filename)
        topology, vertex_count = get_topology_vertexcount(vb0_filename)
        logging.info("当前vb0文件的topology：" + str(topology))
        logging.info("当前vb0文件的vertex_count：" + str(vertex_count))

        if topology == b"pointlist":
            # print("index: " + str(indices[index]) + " VertexCount = " + str(vertex_count))

            # Filter, vb0 filename must have ROOT VS.
            if use_pointlist_tech:
                if root_vs in vb0_filename:
                    pointlist_indices_dict[indices[index]] = vertex_count
            else:
                pointlist_indices_dict[indices[index]] = vertex_count

        ib_filename = glob.glob(indices[index] + '-ib*txt')[0]
        logging.info("当前处理的ib文件：" + ib_filename)

        topology, vertex_count = get_topology_vertexcount(ib_filename)
        logging.info("当前ib文件的topology： "+str(topology))
        logging.info("当前ib文件的vertex_count： "+str(vertex_count))
        logging.info(split_str)

        if topology == b"trianglelist":
            # Filter,ib filename must include input_ib_hash.
            if input_ib_hash in ib_filename:
                topology, vertex_count = get_topology_vertexcount(vb0_filename)
                trianglelist_indices_dict[(indices[index])] = vertex_count
                trianglelist_vertex_count = vertex_count

    logging.info("Based on vertex count, remove the duplicated pointlist indices.")
    logging.info("output pointlist and trianglelist before remove:")
    logging.info(pointlist_indices_dict)
    logging.info(trianglelist_indices_dict)


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
    logging.info("函数：get_pointlit_and_trianglelist_indices执行完成")

    return pointlist_indices, trianglelist_indices


def output_weapon_ini_file(pointlist_indices, input_ib_hash, part_name):
    # info_location = {b"POSITION": "vb0", b"NORMAL": "vb0", b"TANGENT": "vb0",
    #                      b"BLENDWEIGHTS": "vb3",
    #                      b"BLENDINDICES": "vb2",
    #                      b"TEXCOORD": "vb1"}
    logging.info(split_str)
    logging.info("Start to generate "+part_name+"'s ini config file. Type is weapon")
    filenames = sorted(glob.glob(pointlist_indices[0] + '-vb*txt'))

    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]
    logging.info("position_vb: " + str(position_vb))

    texcoord_vb = filenames[1]
    texcoord_vb = texcoord_vb[texcoord_vb.find("-vb1=") + 5:texcoord_vb.find("-vs=")]
    logging.info("texcoord_vb: " + str(texcoord_vb))

    blendindices_vb = filenames[2]
    blendindices_vb = blendindices_vb[blendindices_vb.find("-vb2=") + 5:blendindices_vb.find("-vs=")]
    logging.info("blendindices_vb: " + str(blendindices_vb))

    blendweights_vb = filenames[3]
    blendweights_vb = blendweights_vb[blendweights_vb.find("-vb3=") + 5:blendweights_vb.find("-vs=")]
    logging.info("blendweights_vb: " + str(blendweights_vb))

    output_bytes = b""
    output_bytes = output_bytes + (b"[Resource_POSITION]\r\ntype = Buffer\r\nstride = 40\r\nfilename = " + part_name.encode() + b"_POSITION.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_BLENDINDICES]\r\ntype = Buffer\r\nstride = 4\r\nfilename = " + part_name.encode() + b"_BLENDINDICES.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_BLENDWEIGHTS]\r\ntype = Buffer\r\nstride = 32\r\nfilename = " + part_name.encode() + b"_BLENDWEIGHTS.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_TEXCOORD]\r\ntype = Buffer\r\nstride = 8\r\nfilename = " + part_name.encode() + b"_TEXCOORD.buf\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_IB_FILE]\r\ntype = Buffer\r\nformat = DXGI_FORMAT_R16_UINT\r\nfilename = " + part_name.encode() + b".ib\r\n\r\n")
    output_bytes = output_bytes + (b"[Resource_" + part_name.encode() + b"]\r\nfilename = " + part_name.encode()+b".png\r\n\r\n")

    output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nhandling = skip\r\nib = Resource_IB_FILE\r\n;ps-t7 = Resource_"+ part_name.encode()+b"\r\ndrawindexed = auto\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_TEXCOORD]\r\nhash = "+texcoord_vb.encode()+b"\r\nvb1 = Resource_TEXCOORD\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_BLENDINDICES]\r\nhash = "+blendindices_vb.encode()+b"\r\nvb2 = Resource_BLENDINDICES\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_BLENDWEIGHTS]\r\nhash = "+blendweights_vb.encode()+b"\r\nvb3 = Resource_BLENDWEIGHTS\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_VB_SKIP_1]\r\n;hash = \r\n;handling = skip\r\n\r\n")

    logging.info(part_name + "  generated file content is: ")
    logging.info(str(output_bytes))

    output_file = open("output/"+part_name+".ini", "wb+")
    output_file.write(output_bytes)
    output_file.close()
    logging.info("Generate "+part_name+"'s ini config file completed.")


def output_action_ini_file(pointlist_indices, input_ib_hash, part_name):
    # don't care if pointlist_indices has many candidates,because we only use one of them
    # because they are totally same,just show twice in pointlist files.

    logging.info(split_str)
    logging.info("Start to generate "+part_name+"'s ini config file.")
    filenames = sorted(glob.glob(pointlist_indices[0] + '-vb*txt'))
    position_vb = filenames[0]
    position_vb = position_vb[position_vb.find("-vb0=") + 5:position_vb.find("-vs=")]
    logging.info("position_vb: " + str(position_vb))

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

    output_bytes = output_bytes + (b"[TextureOverride_IB_SKIP]\r\nhash = "+input_ib_hash.encode()+b"\r\nhandling = skip\r\nib = Resource_IB_FILE\r\n;ps-t7 = Resource_"+ part_name.encode()+b"\r\ndrawindexed = auto\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_POSITION]\r\nhash = "+position_vb.encode()+b"\r\nvb0 = Resource_POSITION\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_TEXCOORD]\r\nhash = "+texcoord_vb.encode()+b"\r\nvb1 = Resource_TEXCOORD\r\n\r\n")
    output_bytes = output_bytes + (b"[TextureOverride_BLEND]\r\nhash = "+blend_vb.encode()+b"\r\nvb2 = Resource_BLEND\r\n\r\n")
    output_bytes = output_bytes + (b";[TextureOverride_VB_SKIP_1]\r\n;hash = \r\n;handling = skip\r\n\r\n")

    logging.info(part_name + "  generated file content is: ")
    logging.info(str(output_bytes))

    output_file = open("output/"+part_name+".ini", "wb+")
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


def merge_pointlist_files_v2(pointlist_indices, trianglelist_indices, merge_info=MergeInfo()):
    part_name = merge_info.part_name
    read_pointlist_element_list = merge_info.element_list

    logging.info("Stat execute: merge_pointlist_files_v2")

    logging.info("Start to move ps-t0 files to output folder.")
    move_related_files(trianglelist_indices, move_dds=True, only_pst7=True)
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
    # logging.info("How many ib_file_bytes we finally have?")
    # logging.info(ib_file_bytes.__len__())


    logging.info("Output to file.")
    for index in range(len(ib_file_bytes)):
        output_partname = part_name + str(index)

        ib_file_byte = ib_file_bytes[index]
        output_vbname = "output/" + merge_info.draw_ib + "-" + output_partname + "-vb0.txt"
        output_ibname = "output/" + merge_info.draw_ib + "-" + output_partname + "-ib.txt"
        output_vb_fileinfo.output_filename = output_vbname

        logging.info("Output Step 1: Write to ib file.")
        output_ibfile = open(output_ibname, "wb+")
        output_ibfile.write(ib_file_byte)
        output_ibfile.close()

        logging.info("Output Step 2: Write to vb file.")
        output_vb_file(output_vb_fileinfo)

        logging.info("Output Step 3: Generate ini config file: ")
        if merge_info.type == "weapon":
            output_weapon_ini_file(pointlist_indices, merge_info.draw_ib, output_partname)
        else:
            # TODO remember to use ib_file_first_index_list
            output_action_ini_file(pointlist_indices, merge_info.draw_ib, output_partname)
        logging.info(split_str)


def merge_pointlist_files(pointlist_indices, trianglelist_indices, part_name):
    logging.info("执行函数：merge_pointlist_files")

    logging.debug("开始移动ps-t7文件到output目录：")
    move_related_files(trianglelist_indices, move_dds=True, only_pst7=True)

    logging.debug("开始移动生成的ini文件到output目录：")
    output_action_ini_file(pointlist_indices, merge_info.draw_ib, part_name)

    # The vertex data you want to read from pointlist vb file.
    read_pointlist_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHTS", b"BLENDINDICES"]

    pointlist_vertex_data_chunk_list = read_vertex_data_chunk_list_gracefully(pointlist_indices[0],
                                                                              read_pointlist_element_list)

    # The vertex data you want to read from trianglelist vb file.
    read_trianglelist_element_list = [b"COLOR", b"TEXCOORD", b"TEXCOORD1"]

    final_trianglelist_vertex_data_chunk_list_list = []
    for trianglelist_index in trianglelist_indices:
        vertex_data_chunk_list_tmp = read_vertex_data_chunk_list_gracefully(trianglelist_index,
                                                                            read_trianglelist_element_list,
                                                                            only_vb1=True, sanity_check=True)
        final_trianglelist_vertex_data_chunk_list_list.append(vertex_data_chunk_list_tmp)

    repeat_vertex_data_chunk_list_list = []

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

        if b"TEXCOORD" not in element_name_list:
            continue

        # for vertex_data in first_vertex_data_chunk:
        #     print(vertex_data.element_name)
        #     print(vertex_data.data)
        # print("-----------------------------------")
        repeat_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)

    # Remove duplicated contents.
    final_trianglelist_vertex_data_chunk_list_list = []
    repeat_check = []
    for final_trianglelist_vertex_data_chunk_list in repeat_vertex_data_chunk_list_list:
        # Grab the first one to check.
        first_vertex_data_chunk = final_trianglelist_vertex_data_chunk_list[0]
        first_vertex_data = first_vertex_data_chunk[0]

        # The length of final_trianglelist_vertex_data_chunk_list must equals pointlist_vertex_data_chunk_list's length.
        if len(final_trianglelist_vertex_data_chunk_list) == len(pointlist_vertex_data_chunk_list):
            if first_vertex_data.data not in repeat_check:
                repeat_check.append(first_vertex_data.data)
                final_trianglelist_vertex_data_chunk_list_list.append(final_trianglelist_vertex_data_chunk_list)

    if len(final_trianglelist_vertex_data_chunk_list_list) != 1:
        logging.error("The length after duplicate removal should be 1!")
        exit(1)

    # After duplicate removal, there should only be one element in list,so we use index [0].
    final_trianglelist_vertex_data_chunk_list = final_trianglelist_vertex_data_chunk_list_list[0]

    # Based on output_element_list，generate a final header_info.
    output_element_list = [b"POSITION", b"NORMAL", b"TANGENT", b"BLENDWEIGHTS", b"BLENDINDICES", b"COLOR", b"TEXCOORD", b"TEXCOORD1"]

    header_info = get_header_info_by_elementnames(output_element_list)
    # Set vertex count
    header_info.vertex_count = str(len(final_trianglelist_vertex_data_chunk_list)).encode()

    # Generate a final vb file.
    if len(pointlist_vertex_data_chunk_list) != len(final_trianglelist_vertex_data_chunk_list):
        print(
            "The length of the pointlist_vertex_data_chunk_list and the final_trianglelist_vertex_data_chunk_list should equal!")
        exit(1)

    final_vertex_data_chunk_list = [[] for i in range(int(str(header_info.vertex_count.decode())))]
    for index in range(len(pointlist_vertex_data_chunk_list)):
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + pointlist_vertex_data_chunk_list[
            index]
        final_vertex_data_chunk_list[index] = final_vertex_data_chunk_list[index] + \
                                              final_trianglelist_vertex_data_chunk_list[index]

    # Solve TEXCOORD1 can't match the element's semantic name TEXCOORD problem.
    element_aligned_byte_offsets = {}
    new_element_list = []
    for element in header_info.elementlist:
        print("-----------------")
        print(element.semantic_name)
        print(element.semantic_index)

        element_aligned_byte_offsets[element.semantic_name] = element.aligned_byte_offset
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

    pointlist_indices, trianglelist_indices = get_pointlit_and_trianglelist_indices_V2(merge_info.draw_ib, merge_info.root_vs, use_pointlist_tech=merge_info.use_pointlist)

    if use_pointlist_tech:
        if len(pointlist_indices) == 0:
            logging.error("Can't found any pointlist file,please turn pointlist tech flag to False for ['" + merge_info.part_name + "']")
            exit(1)
        if merge_info.only_pointlist:
            merge_pointlist_files_v2(pointlist_indices, trianglelist_indices, merge_info)
        else:
            merge_pointlist_files(pointlist_indices, trianglelist_indices, merge_info.part_name)
    else:
        logging.info("Only fetch from trianglelist files.")
        merge_trianglelist_files(trianglelist_indices, merge_info.part_name)


if __name__ == "__main__":
    """
    Version V2.1 features:
    Extract to Blender:
    - Can extract some of the weapon item which use ROOT_VS 9684c4091fc9e35a.
    - Can extract some of the decorations item which use ROOT_VS 9684c4091fc9e35a.
    - Can extract body and some of the cloth item which use ROOT_VS e8425f64cfb887cd.
    - Can extract any item from trianglelist topology vb files but without BLEND info.
    
    Import back to game:
    - Can split every types above of vb files but need some ajustment.
    
    Todo list:
    # TODO solve the vertex limit problem,
    #  because we can't correctly replace a object which vertex number is more than original object.
    # TODO add use specific index to read pointlist info.
    # TODO 学习blender shading教程，在blender中正确的渲染出人物。
    # TODO 目前仍无法导出挂饰和固定的衣物部件
    """

    GameName = "Honkai: Star Rail"
    split_str = "----------------------------------------------------------------------------------------------"
    output_folder_name = "output"

    # Here is your Loader location.
    LoaderFolder = "D:/softs/Star Rail/Game/"

    # Set work dir, here is your FrameAnalysis dump dir.
    FrameAnalyseFolder = "FrameAnalysis-2023-04-30-130853"

    # Here is the ROOT VS the game currently use, SR use e8425f64cfb887cd as it's ROOT ACTION VS now.
    # RootActionVS = "e8425f64cfb887cd"
    # RootItemVS = "9684c4091fc9e35a"

    merge_info = MergeInfo()
    merge_info.part_name = "body"
    merge_info.type = "cloth"
    merge_info.root_vs = "e8425f64cfb887cd"
    merge_info.draw_ib = "97ad7623"
    merge_info.use_pointlist = True
    merge_info.only_pointlist = True

    # TODO 输入时指定ELEMENT元素的各种属性，包括输出的长度
    merge_info.element_list = [b"POSITION", b"NORMAL", b"TANGENT"
                               , b"COLOR",b"TEXCOORD",b"TEXCOORD1"
                               ,b"BLENDWEIGHTS", b"BLENDINDICES"]

    # Remember this location must be manually write.
    # 注意这里的顺序就是最终VB0文件中的顺序！
    info_location_cloth = {b"POSITION": "vb0", b"NORMAL": "vb0", b"TANGENT": "vb0",
                     b"COLOR": "vb1",b"TEXCOORD": "vb1",b"TEXCOORD1": "vb1",
                     b"BLENDWEIGHTS": "vb2", b"BLENDINDICES": "vb2"
                    }

    # TODO 设置一下武器的location信息
    info_location_weapon = {b"POSITION": "vb0", b"NORMAL": "vb0", b"TANGENT": "vb0",
                           b"COLOR": "vb1", b"TEXCOORD": "vb1", b"TEXCOORD1": "vb1",
                           b"BLENDWEIGHTS": "vb2", b"BLENDINDICES": "vb2"
                           }

    merge_info.info_location = info_location_cloth

    # work dir
    work_dir = LoaderFolder + FrameAnalyseFolder + "/"

    # switch to work dir.
    os.chdir(work_dir)
    if not os.path.exists('output'):
        os.mkdir('output')

    # set the output log file.
    logging.basicConfig(filename=work_dir + "output/" + str(time.strftime('%Y-%m-%d_%H_%M_%S_')) + str(time.time_ns()) + '.log', level=logging.DEBUG)

    logging.info("HSR MergeScript Current Version V2.1")
    logging.info("Switch to work dir: " + work_dir)
    logging.info(split_str)

    logging.info("Current Game: " + GameName)
    logging.info("Set RootVS To: " + merge_info.root_vs)
    logging.info("Set LoaderFolder To:" + LoaderFolder)
    logging.info("Set FrameAnalyseFolder To: " + FrameAnalyseFolder)
    logging.info("Set work dir to: " + work_dir)
    logging.info(split_str)

    logging.info("Start to process hash: " + merge_info.draw_ib)
    logging.info("Current hash's part name: " + merge_info.part_name)

    use_pointlist_tech = merge_info.use_pointlist
    logging.info("Whether current object use Pointlist Topology: " + str(use_pointlist_tech))

    start_merge_files(merge_info)
    logging.info(split_str)

    logging.info("----------------------------------------------------------\r\nAll process done！")



