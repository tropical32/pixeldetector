import os
import argparse
import time
from PIL import Image
import numpy as np
import scipy
from itertools import product
from collections import defaultdict

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="Path to input image")
ap.add_argument("-o", "--output", required=False, default="output.png", help="Path to save output image")
ap.add_argument("-m", "--max", required=False, type=int, default=128, help="Max colors for automatic palette detection")
ap.add_argument("-p", "--palette", required=False, action="store_true", help="Automatically reduce colors using elbow method")
ap.add_argument("-c", "--colors", required=False, type=int, help="Exact number of colors for output (overrides -p)")
ap.add_argument("-s", "--size", required=False, type=int, nargs=2, help="Desired output dimensions as width height")
args = vars(ap.parse_args())

def kCentroid(image: Image, width: int, height: int, centroids: int):
    has_alpha = image.mode == 'RGBA'
    image = image.convert("RGBA" if has_alpha else "RGB")
    downscaled = np.zeros((height, width, 4 if has_alpha else 3), dtype=np.uint8)
    wFactor = image.width/width
    hFactor = image.height/height

    for x, y in product(range(width), range(height)):
        tile = image.crop((x*wFactor, y*hFactor, (x*wFactor)+wFactor, (y*hFactor)+hFactor))
        
        if has_alpha:
            rgb_tile = tile.convert("RGB")
            alpha_channel = np.array(tile.getchannel('A'))
            quantized_rgb = rgb_tile.quantize(colors=centroids, method=1, kmeans=centroids).convert("RGB")
            color_counts = quantized_rgb.getcolors()
            most_common = max(color_counts, key=lambda x: x[0])[1]
            
            matching_pixels = np.all(np.array(quantized_rgb) == most_common, axis=2)
            alpha_values = alpha_channel[matching_pixels]
            
            if alpha_values.size > 0:
                alpha_count = defaultdict(int)
                for a in alpha_values:
                    alpha_count[a] += 1
                best_alpha = max(alpha_count.items(), key=lambda x: x[1])[0]
            else:
                best_alpha = 255
            
            downscaled[y, x, :] = (*most_common, best_alpha)
        else:
            quantized = tile.quantize(colors=centroids, method=1, kmeans=centroids).convert("RGB")
            color_counts = quantized.getcolors()
            most_common = max(color_counts, key=lambda x: x[0])[1]
            downscaled[y, x, :] = most_common

    return Image.fromarray(downscaled, mode='RGBA' if has_alpha else 'RGB')

def pixel_detect(image: Image):
    npim = np.array(image.convert("RGB"))[..., :3]

    hdiff = np.sqrt(np.sum((npim[:, :-1, :] - npim[:, 1:, :])**2, axis=2))
    hsum = np.sum(hdiff, 0)

    vdiff = np.sqrt(np.sum((npim[:-1, :, :] - npim[1:, :, :])**2, axis=2))
    vsum = np.sum(vdiff, 1)

    hpeaks, _ = scipy.signal.find_peaks(hsum, distance=1, height=0.0)
    vpeaks, _ = scipy.signal.find_peaks(vsum, distance=1, height=0.0)
    
    hspacing = np.diff(hpeaks)
    vspacing = np.diff(vpeaks)

    return kCentroid(image, round(image.width/np.median(hspacing)), round(image.height/np.median(vspacing)), 2), np.median(hspacing), np.median(vspacing)

def determine_best_k(image: Image, max_k: int):
    has_alpha = image.mode == 'RGBA'
    rgb_image = image.convert("RGB") if has_alpha else image
    pixels = np.array(rgb_image)
    pixel_indices = np.reshape(pixels, (-1, 3))

    distortions = []
    for k in range(1, max_k + 1):
        quantized_image = rgb_image.quantize(colors=k, method=0, kmeans=k, dither=0)
        centroids = np.array(quantized_image.getpalette()[:k * 3]).reshape(-1, 3)
        
        distances = np.linalg.norm(pixel_indices[:, np.newaxis] - centroids, axis=2)
        min_distances = np.min(distances, axis=1)
        distortions.append(np.sum(min_distances ** 2))

    rate_of_change = np.diff(distortions) / np.array(distortions[:-1])
    elbow_index = np.argmax(rate_of_change) + 1 if len(rate_of_change) > 0 else 0
    return max(2, elbow_index + 2)

if os.path.isfile(args["input"]):
    image = Image.open(args["input"]).convert('RGBA')
    start = round(time.time()*1000)

    if args["size"] is not None:
        target_width, target_height = args["size"]
        downscale = kCentroid(image, target_width, target_height, 2)
        print(f"Resized to {target_width}x{target_height} in {round(time.time()*1000)-start}ms")
    else:
        downscale, _, _ = pixel_detect(image)
        print(f"Auto-sized to {downscale.width}x{downscale.height} in {round(time.time()*1000)-start}ms")

    output = downscale

    # Color reduction logic
    if args["colors"] or args["palette"]:
        start = round(time.time()*1000)
        
        if args["colors"]:
            best_k = max(1, args["colors"])
            print(f"Quantizing to exactly {best_k} colors")
        else:
            best_k = determine_best_k(downscale, args["max"])
            print(f"Auto-reduced to {best_k} colors")

        if downscale.mode == 'RGBA':
            rgb_image = downscale.convert('RGB')
            quantized = rgb_image.quantize(colors=best_k, method=1, kmeans=best_k, dither=0)
            quantized = quantized.convert('RGBA')
            quantized.putalpha(downscale.getchannel('A'))
        else:
            quantized = downscale.quantize(colors=best_k, method=1, kmeans=best_k, dither=0)
        
        output = quantized
        print(f"Color reduction completed in {round(time.time()*1000)-start}ms")

    output.save(args["output"], format="PNG", optimize=True)
else:
    print("no input")
