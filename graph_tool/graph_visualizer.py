from graph_tool.all import *
from graph_tool import draw, community
import matplotlib

# Parameters.
link_file = 'outlet_links.tsv'
label_file = 'outlets.tsv'
output_file = 'directed_unweighted_outlets_2_communities.png'
files_are_zero_indexed = True
min_outgoing_edges = 3
num_communities = 2

g = Graph()

# Adds a vertex to the graph for each row in label_file, and stores the vertex's label as a vertex property.
labels = g.new_vertex_property('string')
with open(label_file) as f:
    for line in f.readlines():
        vertex_id, vertex_label = line.strip().split('\t', 1)
        vertex = g.add_vertex()
        labels[vertex] = vertex_label

# Adds an edge to the graph for each row in link_file.
weights = g.new_edge_property('float')
with open(link_file) as f:
    for line in f.readlines():
        src, dst, weight = line.strip().split('\t')
        src_id = int(src)
        dst_id = int(dst)
        if not files_are_zero_indexed:
            src_id -= 1
            dst_id -= 1
        if src_id != dst_id:
            edge = g.add_edge(g.vertex(src_id), g.vertex(dst_id))
            weights[edge] = float(weight)

# Removes all vertices (and associated edges) that have fewer than min_outgoing_edges outgoing edges.
print('Num total vertices: %d' % g.num_vertices())
vertices_to_remove = []
for vertex in g.vertices():
    has_out_edge = False
    if sum([1 for _ in vertex.out_edges()]) < min_outgoing_edges:
        vertices_to_remove.append(vertex)
g.set_fast_edge_removal()
g.remove_vertex(vertices_to_remove)
print('Num vertices: %d' % g.num_vertices())

# Cluster the vertices into communities.
state = community.BlockState(g, B=g.num_vertices(), deg_corr=True)
state = community.multilevel_minimize(state, B=num_communities)

# Compute the position of each vertex.
pos = sfdp_layout(g)
#pos = sfdp_layout(g, vweight=state.get_blocks())
#pos = draw.arf_layout(g, max_iter=0, weight=weights)
#pos = draw.radial_tree_layout(g, g.vertex(g.num_vertices() - 1))

# Saves the graph image to output_file as a .png.
graph_draw(g, pos, output_size=(1500, 1500),
           #vcmap=matplotlib.cm.gist_heat_r,
           edge_pen_width=5,
           vertex_text=labels,
           vertex_font_size=14,
           vertex_size=30,
           vertex_fill_color=state.get_blocks(),
           output=output_file)


# Print out sources in each community.
# for community_id in xrange(num_communities):
