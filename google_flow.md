# Google Flow Features

## 1. Overview
Google Flow (accessed via Google Labs) is an AI filmmaking tool designed for creators, leveraging Google’s most advanced generative models (Veo, Imagen, Gemini) to create cinematic clips, scenes, and stories with consistency.

## 2. Main Interface & Project Management
The workspace is built around an infinite scroll canvas where assets are displayed as a gallery.
- **Project Structure**: Everything is contained within a "Project". You can rename, delete, and duplicate whole projects.
- **Grid Settings**: You can view your generated content as a standard Grid or in "Batch" view. The tile size can be adjusted (Small, Medium, Large) to fit more or fewer generations on the screen.
- **Add Multimedia (+)**: You can upload your own reference images or create "Collections" to group similar outputs.

## 3. Scene Creator and Editing
Flow provides a non-linear editing interface (Scenebuilder) to combine clips into a cohesive story.
- **Timeline Organization**: Drag and drop previously generated images or video clips onto the timeline to reorder them and produce a final Scene.
- **In-Video Editing (Generative Refinement)**:
  - **Insert Object**: By drawing a bounding box on a frame and providing a prompt, you can add new elements to an existing scene.
  - **Remove Object**: Drawing a box around an unwanted element allows Flow to remove it seamlessly.

## 4. Multimedia Generation Settings
The generation interface offers versatile creation controls:

### Prompts and Attachments
The prompting bar allows you to type what you want to create. By clicking the **+** button next to the input field, you can add structural rules or insert reference images to guide the generation style.

### Model Selection and Quantity
Users have access to multiple AI models depending on the need:
- **Nano Banana 2 / Nano Banana Pro**: Standard and advanced models for high-quality image generation.
- **Imagen 4**: Google's premier high-fidelity image generation model.
- **Veo Models**: Advanced models for generating video.
- **Quantity Selector**: You can tweak how many variations the AI produces per prompt (from x1 up to x4).

## 5. Post-Generation Image Actions
Once an image is generated, hovering over it reveals quick actions (like adding it to a scene or re-rolling). Clicking the **More (...)** menu exposes advanced workflows:
- **Animuj (Animate)**: Convert a static AI image into a short motion video.
- **Dodaj do prompta (Add to Prompt)**: Use the generated image as an input reference for the next cycle, allowing iterative refinement of a concept.
- **Użyj prompta ponownie (Reuse Prompt)**: Brings the exact prompt back to the input bar.
- **Organizational Tools**: You can *Favorite*, *Download (Pobierz)*, *Rename*, or *Copy* individual assets.

## 6. Video Creation Features
In addition to static images, Flow supports robust video generation powered by advanced models like **Veo 3.1**. You can access video features by toggling the generation mode from "Image" to "Video" in the prompt bar.

### First Frame and Last Frame (Rozpocznij & Koniec)
- **Keyframe Control**: When in video mode, the interface displays two placeholders typically labeled "Rozpocznij" (Start) and "Koniec" (End).
- **Functionality**: These act as the first frame and last frame of the video. You can click on them to select an image from your existing Flow project assets or upload a new one. This ensures the generated video perfectly connects point A to point B.
- **Swap**: There is a swap icon to instantly reverse the start and end frames.

### Expand Clip
- **Purpose**: This allows you to extend a short, generated video clip into a longer sequence.
- **Location**: You can find "Expand" in two main areas:
  1. Hovering over a generated video tile in the main grid and opening the "More (...)" menu often reveals an option to expand or extend the video.
  2. Inside the **Scene Creator** timeline, adding a clip allows you to drag to expand or use tools to extend the duration based on the video's last frame.

### Annotations and Ingredients (Motion Brush, Regional Controls)
- **Ingredients Menu**: Within the video settings (the "Film" button next to models), there is an "Ingredients" tab.
- **Regional Prompting/Annotations**: You can "annotate" specific regions of the start frame. This acts as a "Motion Brush" where you define exactly which area of the image should move and how, leaving the rest static.
- **Locking Elements**: Ingredients allow you to lock particular characters or styles to maintain consistency throughout the video generation. You can drag and drop existing project assets (or type `@`) into the prompt to serve as Ingredients.

### Advanced Video Actions
- **Camera Control**: For the cinematic feel, users have control over **Pan** (horizontal), **Tilt** (vertical), **Zoom**, and **Roll** (rotation). 
- **Audio Generation (Experimental)**: Available primarily on **Veo 3.1**, users can prompt for audio (e.g., "sounds of flying cars") which the AI will generate alongside the video track.

## 7. Practical Video Evaluation
A practical browser test of video generation using the **Veo 3.1 - Fast** model revealed the following operational realities:

### Generation Speed and Feedback
When submitting a single video generation (x1) using a static image as the "First Frame" and a text prompt guiding the motion:
- A progress tile provides percentage updates in real-time.
- The entire generation process for a standard short clip using a "Fast" model takes roughly **1 minute and 5 seconds** (tested via browser automation).
- The resulting video perfectly connects the uploaded first frame to the prompted motion with high visual consistency. The output features a persistent "Veo" watermark in the corner.

### In-Video Dedicated Editor
Clicking "Edit" on a successfully generated video opens a dedicated player/editor interface distinct from the main grid. This interface contains four primary modification tools, each altering the prompt bar behavior when selected:

#### 1. Expand (Rozszerz)
- **Function**: Designed to continue the action of a video clip or extend its duration from the last frame.
- **UI Interaction**: When clicked, the prompt bar changes to **"What next? (Co dalej?)"**. The user describes the continuing action, and the AI generates a seamless extension adding a new segment to the sequence.

#### 2. Insert (Wstaw)
- **Function**: Used for local editing, adding specific elements to existing video frames (similar to generative in-painting for video).
- **UI Interaction**: The prompt bar instructs the user to *describe what to add* and provides an interactive option to *click and drag on the video frame* to specify the exact location for the new element.

#### 3. Erase (Usuń)
- **Function**: Operates as the inverse of Insert, allowing users to highlight an object in the video and instruct the AI to remove it seamlessly from the sequence.

#### 4. Camera (Kamera)
- **Function**: Provides advanced control over virtual cinematography through curated, high-quality presets.
- **UI Interaction**: It is divided into two tabs featuring visual thumbnail previews:
  - **Camera Motion (Ruch kamery)**: Offers dynamic movements like Zoom in/out (Najazd/Odjazd kamerą), circular Orbit tracking, and complex Dolly-Zoom effects.
  - **Camera Position (Pozycja kamery)**: Sets the static framing, offering Horizontal alignment (Center, Left, Right), Vertical angle (High, Low), and Depth (Close-up, Wide shot).

## 8. Scene Creator (Kreator Scen) & Timeline
The Scene Creator allows users to sequence multiple generated clips together into a cohesive final video.

### Adding Clips to the Scene
A crucial workflow detail: Clips **are not** drag-and-dropped from an asset bin while inside the Scene Creator. Instead, they must be added from the main project gallery:
1. Locate the generated clip in the grid.
2. Click the three dots `...` (More Options) on the clip.
3. Select **"Dodaj do sceny" (Add to scene)**.

### Timeline Mechanics
Once clips are added to the scene, opening the Scene Creator (via the filmstrip icon) reveals a bottom-anchored timeline:
- **Trimming**: Clicking on a clip within the timeline activates yellow trimming handles on the left and right edges, allowing users to precisely shorten the start or end of a specific generation without re-rendering.
- **Reordering**: The timeline fully supports intuitive drag-and-drop operations to change the sequential order of the clips.
- **Playback & Arrangement**: The interface includes playback controls to preview the combined sequence and arrangement tools ("Rozmieść") to manage how clips transition.

Ultimately, the Scene Creator serves as a lightweight, non-destructive NLE (Non-Linear Editor) built directly into the generative environment, streamlining the process of creating complete short films from individual prompts.
