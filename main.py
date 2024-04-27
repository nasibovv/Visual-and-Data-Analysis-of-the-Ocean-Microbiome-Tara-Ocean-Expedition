import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


# Load and preprocess the dataset
data_path = 'combined_Tara_Data.csv'
tara_data = pd.read_csv(data_path).replace('undef', pd.NA).dropna()

# Combine several Plotly qualitative color palettes
all_palettes = [
    px.colors.qualitative.Dark24,
    px.colors.qualitative.Alphabet,
    px.colors.qualitative.Light24,
    px.colors.qualitative.Safe,
    px.colors.qualitative.Set1,
    px.colors.qualitative.Pastel,
    px.colors.qualitative.Bold,
    px.colors.qualitative.Pastel2,
    px.colors.qualitative.Set2,
    px.colors.qualitative.Set3,
    px.colors.qualitative.Antique,
    px.colors.qualitative.Prism,
]

# Flatten the list of palettes into one extended palette
extended_palette = [color for palette in all_palettes for color in palette]

# Ensure the extended palette is large enough for all unique genera
color_sequence = extended_palette * ((len(tara_data['Genus'].unique()) // len(extended_palette)) + 1)

# Extend the color sequence to ensure there are enough unique colors
#color_sequence = px.colors.qualitative.Dark24 * ((len(tara_data['Genus'].unique()) // len(px.colors.qualitative.Dark24)) + 1)

# Visualization 1: Top 20 Microbiome Average Abundance by Selected Ocean and Sea Region
fig = go.Figure()

# Create a color mapping for each genus
color_map = {genus: color_sequence[i] for i, genus in enumerate(tara_data['Genus'].unique())}

for region in tara_data['OceanAndSeaRegion'].unique():
    region_data = tara_data[tara_data['OceanAndSeaRegion'] == region]
    region_average_abundance = region_data.groupby(['Genus'])['Abundance'].mean().reset_index()
    top_microbiomes_region = region_average_abundance.nlargest(20, 'Abundance')
    
    # If there are less than 20, pad the remaining with empty strings and zeros
    if len(top_microbiomes_region) < 20:
        top_up = pd.DataFrame({'Genus': [''] * (20 - len(top_microbiomes_region)), 'Abundance': [0] * (20 - len(top_microbiomes_region))})
        top_microbiomes_region = pd.concat([top_microbiomes_region, top_up], ignore_index=True)
    
    # Assign unique colors to each bar based on genus
    fig.add_trace(
        go.Bar(
            y=top_microbiomes_region['Genus'],
            x=top_microbiomes_region['Abundance'],
            name=region,
            orientation='h',
            marker=dict(color=[color_map[genus] for genus in top_microbiomes_region['Genus']]),  # Use the color mapping here
            visible=(region == tara_data['OceanAndSeaRegion'].unique()[0])
        )
    )

# Update the layout of Visualization 1
fig.update_layout(
    title_text="Top 20 Microbiome Average Abundance by Selected Ocean and Sea Region",
    xaxis=dict(title="Average Abundance"),
    yaxis=dict(title="Microbiome (Genus)", autorange='reversed'),
    updatemenus=[{
        'buttons': [
            {
                'args': ['visible', [region == r for r in tara_data['OceanAndSeaRegion'].unique()]],
                'label': region,
                'method': 'restyle'
            } for region in tara_data['OceanAndSeaRegion'].unique()
        ],
        'direction': 'down',
        'pad': {"r": 10, "t": 10},
        'showactive': True,
        'x': 0.5,
        'xanchor': 'center',
        'y': 1.15,
        'yanchor': 'top'
    }],
    barmode='stack',
    margin=dict(t=60, b=150),
    #showlegend=True  # Show legend
)

# Visualization 2: Overall Abundance Patterns by Taxonomic Level
taxonomic_levels = ['Domain','Phylum', 'Class', 'Order', 'Family', 'Genus']  # Define your taxonomic levels
fig1 = go.Figure()

# Function to add bars for a given taxonomic level
def add_bars_for_taxonomic_level(level, visible=False):
    level_data = tara_data.groupby(level)['Abundance'].sum().reset_index()
    level_data = level_data.nlargest(10, 'Abundance')  # Get top 10 for clarity in visualization
    # Use a new color sequence specifically for Visualization 2 if needed
    level_colors = color_sequence[:len(level_data[level])]
    fig1.add_trace(go.Bar(
        x=level_data[level], 
        y=level_data['Abundance'],
        name=level,
        marker=dict(color=level_colors),  # Assign colors from the level-specific color sequence
        visible=visible
    ))

# Add bars for each level, making only 'Genus' visible by default
for level in taxonomic_levels:
    add_bars_for_taxonomic_level(level, visible=(level == 'Genus'))

# Update figure layout with a dropdown menu to switch between taxonomic levels
fig1.update_layout(
    updatemenus=[{
        'buttons': [
            {
                'label': level,
                'method': 'update',
                'args': [{'visible': [l.name == level for l in fig1.data]},
                         {'title': f'Overall Abundance Patterns by {level}',
                          'xaxis': {'title': level},
                          'yaxis': {'title': 'Abundance'}}]
            } for level in taxonomic_levels
        ],
        'direction': 'down',
        'pad': {'r': 10, 't': 10},
        'showactive': True,
        'x': 0.5,
        'xanchor': 'center',
        'y': 1.15,
        'yanchor': 'top'
    }],
    title='Overall Abundance Patterns by Genus',
    xaxis={'title': 'Genus'},
    yaxis={'title': 'Abundance'},
    #showlegend=True
)

# Visualization 3: Abundance Patterns vs. Metadata
sample_genus = top_genera[0]
fig2 = px.scatter(abundance_by_genus[abundance_by_genus['Genus'] == sample_genus],
                  x='SamplingDepth[m]', y='Abundance', color='MarinePelagicBiomes',
                  title=f"Abundance of {sample_genus} Across Depths and Biomes",
                  hover_data=['SampleID', 'Abundance'])

# Visualization 4: Comparative Diversity Across Taxonomic Levels with custom colors
abundance_by_phylum = tara_data.groupby(['Phylum', 'MarinePelagicBiomes', 'SamplingDepth[m]'])['Abundance'].sum().reset_index()
fig3 = px.scatter(abundance_by_phylum, x='SamplingDepth[m]', y='Abundance', color='Phylum',
                  title="Comparative Microbial Diversity Across Phyla and Depths",
                  labels={'Phylum': 'Taxonomic Phylum'},
                  color_discrete_sequence=color_sequence[:len(abundance_by_phylum['Phylum'].unique())],
                  hover_data=['Phylum', 'Abundance'])

# Visualization 5: Sample Comparison (parallel coordinates)
sample_comparison = tara_data[tara_data['SampleID'].isin(tara_data['SampleID'].unique()[:10])]
fig4 = px.parallel_coordinates(sample_comparison, color='Abundance',
                               dimensions=['SamplingDepth[m]', 'Latitude[degreesNorth]', 'Longitude[degreesEast]', 'Abundance'],
                               title="Sample Comparison",
                               labels={'SamplingDepth[m]': 'Depth (m)', 'Latitude[degreesNorth]': 'Latitude', 'Longitude[degreesEast]': 'Longitude', 'Abundance': 'Abundance'})


# Prepare data for Sankey diagrams
# Aggregating data at Domain level
domain_layer_data = tara_data.groupby(['Domain', 'Phylum', 'LayerOfOrigin'])['Abundance'].sum().reset_index()

# Creating unique lists for domains, phyla, and layers
domain_list = domain_layer_data['Domain'].unique().tolist()
phylum_list = domain_layer_data['Phylum'].unique().tolist()
layer_list = domain_layer_data['LayerOfOrigin'].unique().tolist()

# Generating mappings
domain_mapping = {domain: i for i, domain in enumerate(domain_list)}
phylum_mapping = {phylum: len(domain_list) + i for i, phylum in enumerate(phylum_list)}
layer_mapping = {layer: len(domain_list) + len(phylum_list) + i for i, layer in enumerate(layer_list)}

# Generating source, target, and value for domains and phyla
source = [domain_mapping[row['Domain']] for _, row in domain_layer_data.iterrows()]
target = [phylum_mapping[row['Phylum']] for _, row in domain_layer_data.iterrows()]
value = domain_layer_data['Abundance'].tolist()

# Aggregating data at Class level
class_layer_data = tara_data.groupby(['Phylum', 'Class', 'LayerOfOrigin'])['Abundance'].sum().reset_index()

# Creating unique list for classes
class_list = class_layer_data['Class'].unique().tolist()

# Generating mappings
class_mapping = {cls: len(domain_list) + len(phylum_list) + len(layer_list) + i for i, cls in enumerate(class_list)}

# Generating source, target, and value for phyla and classes
source_class = [phylum_mapping[row['Phylum']] for _, row in class_layer_data.iterrows()]
target_class = [class_mapping[row['Class']] for _, row in class_layer_data.iterrows()]
value_class = class_layer_data['Abundance'].tolist()

# Combining all labels
all_labels = domain_list + phylum_list + layer_list + class_list

# Create the Sankey diagrams with hovertemplate included
# Define a color palette for nodes
node_palette = px.colors.qualitative.Set2  

# Assign colors to nodes based on their index
node_colors = [node_palette[i % len(node_palette)] for i in range(len(all_labels))]

# Create the Sankey diagram for Domain-Phylum-Layer
fig5 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=all_labels,
        color=node_colors
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=[node_colors[src] for src in source] 
    )
)])

# Create the Sankey diagram for Phylum-Class-Layer
fig6 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=15,
        line=dict(color="black", width=0.5),
        label=all_labels,
        color=node_colors
    ),
    link=dict(
        source=source_class,
        target=target_class,
        value=value_class,
        color=[node_colors[src] for src in source_class]  # Apply colors to links
    )
)])

# Update hover information with more descriptive text
fig5.data[0].link.hovertemplate = 'Source: %{source.label}<br>Target: %{target.label}<br>Count: %{value}<extra></extra>'
fig6.data[0].link.hovertemplate = 'Source: %{source.label}<br>Target: %{target.label}<br>Count: %{value}<extra></extra>'


# Function to create a div element from a Plotly figure
def fig_to_div_string(fig):
    return pio.to_html(fig, full_html=False)

# Combine the div elements for each figure into a single HTML string
combined_html = f"""
<html>
<head>
<title>Combined Visualizations</title>
</head>
<body>
    <h1>Visualization 1: Top 20 Microbiome Average Abundance</h1>
    {fig_to_div_string(fig)}
    <h1>Visualization 2: Overall Abundance Patterns</h1>
    {fig_to_div_string(fig1)}
    <h1>Visualization 3: Abundance of Top Genus Across Depths and Biomes</h1>
    {fig_to_div_string(fig2)}
    <h1>Visualization 4: Comparative Microbial Diversity Across Phyla and Depths</h1>
    {fig_to_div_string(fig3)}
    <h1>Visualization 5: Sample Comparison</h1>
    {fig_to_div_string(fig4)}
    <h1>Visualization 6: Sankey Diagram at Domain Level</h1>
    {fig_to_div_string(fig5)}
    <h1>Visualization 7: Sankey Diagram at Class Level</h1>
    {fig_to_div_string(fig6)}
</body>
</html>
"""

# Write the combined HTML string to a file
output_file = 'combined_visualizations_v8.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(combined_html)