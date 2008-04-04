                         Massive Importer for Maya 8.5

                         www.NimbleStudiosInc.com

                         info@nimblestudiosinc.com

Import skinned and textured Massive simulations into Maya

Elements Supported
==================
o Plug-in has been tested on Linux and Windows, and may work on OSX
o Agent skeletons and segment shapes
o AMC and APF simulation data
o Geometry and skin weights
o Materials (currently treated as Maya blinn or lambert shaders)
o Some variables:
  o those used to scale the agent or its segments
  o those embedded in texture file names
  o those used to drive Choice nodes

Known Limitations
=================
o Only supported for Maya 8.5
o Cloth/Lights/Cameras are not imported
o All materials are treated as Maya lambert or blinn shaders (no RenderMan,
  MentalRay, or Velocity support)
o It can take a loooong time to import a scene
o Maya is not set up to handle the same complexity and size scenes as Massive
  is, nor does the importer use massive.so or anything like it, so you may run
  out of memory during an import.


Questions/Bugs/Suggestions
==========================
Feel free to contact us at info@NimbleStudiosInc.com


*******************************************************************************
***                               Instructions                              ***
*******************************************************************************

In Massive
==========

1. Save the skin weights to a weights file for all geometry nodes
2. Save a callsheet for the setup
3. Run a sim using .apf or .amc

In Maya 8.5
===========

1. Load the NimbleMsv.py Python plug-in
2. Run the MEL script 'nsImportMsvWin' to launch the Massive Import window

Massive Import Options
======================

Setup File (required):	   the .mas file to load
Sim Directory (required):  the directory containing the .amc or .apf sim data
Callsheet (optional):      the callsheet to load agent variables from. If a
                           If no callsheet is specified variables will be
                           assigned a random value by the importer (one which
                           almost certainly differs from the value used in
                           Massive).
Sim Type:                  the importer will only load sim data of this file
                           type

Load Geometry:             check this if you want to load the skinned agent
                           geometry
Load Segment Shapes:       check this if you want to load the tube/sphere/cube
                           agent segment shapes
Load Materials:            check this if you want to load the geometry
                           materials.
Skin Type:                 "smooth" skinning will smoothly bind the geometry
                           to the skeleton and resembles the skinning seen in
                           Massive.
                           "chunk" skinning will chop up each piece of
                           geometry into many pieces. Each of these chunks
                           will be parented to a joint. The result is
                           definitely not final render quality, but uses less
                           memory than "smooth" skinning, and looks closer to
                           the final render than using segment shapes.
Load Materials As:         currently the importer does not support RenderMan or
                           MentalRay - all materials will be loaded as either
                           Maya blinn or lambert shaders
Instance Segments:         when loading segment shapes you have the option of
                           instancing every shape, or duplicating it.
                           Instancing will minimize the amount of RAM required,
                           but increases the load time. Duplicating loads
                           quicker but takes up more RAM
Frame Step:                how finely to sample the sim animation data. A frame
                           step of 1 loads every frame of data, a frame step of
                           2 loads every other frame of animation data. In many
                           setups animation data will consume the lion's share
                           of RAM. If the scene is too heavy for Maya to handle
                           you can try increasing the frame step.
                           step.

Caching:                   Enabling will use Maya's Geometry Cache to cache
                           the agent skin deformations to disk. When combined
                           with the "Delete Skeleton" option this can
                           significantly reduce the amount of memory required
                           to import a Massive sim. It will also significantly
                           increase the amount of time required to import.
                           Caching is only valid with the "smooth" skin type.
Delete Skeleton:           If this option is enabled, each agent's skeleton,
                           skin deformers, animation curves, and segments will
                           be deleted after the deformations are cached. This
                           will reduce the amount of memory required to load
                           a sim.
Cache Dir:                 The directory that the Geometry Cache files will be
                           saved in. If left blank it will default to the
                           data/cache directory of the current project.

Selections:                you can choose to load all agents in the setup, or,
                           if you have defined locator selections in Massive,
                           you can tell the importer to only load those agent
                           in the specified selections.

Memory Management Tips
======================

o Enabling Geometry Caching and the Delete Skeletons options yield the best
  results and memory usage.
o If a sim is too large to import all at once, try using the Selections option
  to import it in groups.
o After you import a sim, save it as a Maya scene file, quit and restart Maya,
  and then load the scene file. The memory usage should be much lower than
  when the sim was first imported. You can use this technique along with the
  Selections option to import a large sim in groups - save each group as its
  own Maya scene file, and then import all of the Maya scene files later.
o Increasing the Frame Step can speed up load time and reduce memory usage -
  however the animation quality of the resulting sim may be degraded. If you
  can wait for the long import time, it is better to enable Geometry Caching and
  Delete Skeletons.
o Using the "chunk" Skin Type will speed up load and play back time. It also
  consumes less memory than a non-cached "smooth" skin type. The visual
  quality, however, is greatly degraded. Again, if you can spare the time and
  disk space, it is better to enable Geometry Caching and Delete Skeletons.
