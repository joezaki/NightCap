from allensdk.core.reference_space_cache import ReferenceSpaceCache

# Set your desired resolution in microns (25 is a good balance)
resolution = 25

# Initialize cache for the Allen CCF 2017 brain atlas
rspc = ReferenceSpaceCache(resolution=resolution, reference_space_key='ccf_2017')

# Download and load the reference space
reference_space = rspc.get_reference_space()

print("Atlas loaded!")
