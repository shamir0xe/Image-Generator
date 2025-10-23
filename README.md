# image-generator
Cool project to help you hang your favorite movies on your wall :)

## Manual

Copy `sample.env` into the `.env` and modify its values.

Available options are:
* movie_path: Path of the movie
* image_path: Path of the target image
* movie_frames_path: Path where the frames would be store
* frame_count_per_box: Maximum number of times a frame can appear in the result picture
* final_box_height: The height of the final boxes (frames) in the result picture
* box: How many frames should be located on top of each other on each column
* ratio: Ratio of the movie frames (width / height)
* alpha\[blend\]: How much the frame should be itself: (0, 1)
* beta\[blend\]: How much the frame should fade into the target picture


1) You need to generate movie frames for the specific movie for the first time:
```bash
python main.py gen --movie-name "Paris Texas" --movie-format "mkv" --generate-frames
```

After that, you can omit the "--generate-frames" flag.
You can remove the resulted frames in the output directory. But keep in mind that don't add new ones to the folder, if you do so you need to manually remove the `{movie_name}.csv` file located at the `assets/` folder.

2) If something went wrong, just remove the cache for the specific movie:

```bash
python main.py clear-cache --movie-name "Paris Texas"
```

3) \[TODO:\] `modify` command for some cool features!


