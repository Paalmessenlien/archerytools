# Guide Illustrations Specifications

This document contains detailed specifications for creating illustrations for the archery guides. These can be used with AI image generators or given to illustrators.

## Style Guidelines

- **Style**: Clean, technical illustration style (similar to instructional manuals)
- **Colors**: Use the guide color scheme - Blue for draw length, Green for bow weight, Purple for sight setup, Orange for grip & stance
- **Background**: White or light gray background for clarity
- **Perspective**: Side view for most techniques, front view where specified
- **Details**: Include measurement lines, arrows pointing to key areas, labels

---

## Draw Length Guide Illustrations

### 1. Wingspan Method Illustration
**Prompt**: "Technical illustration showing a person with arms fully extended horizontally, measuring tape stretched between fingertips, clean instructional style, side view, white background, measurement arrows and labels"

**Key Elements**:
- Person standing with arms fully extended
- Measuring tape clearly visible from fingertip to fingertip
- Measurement arrows and dimension lines
- Labels pointing to "Fingertip to fingertip" and "Divide by 2.5"

### 2. Wall Method Illustration
**Prompt**: "Technical diagram showing person against wall with arm extended, measuring from wall to nocking point, instructional manual style, clean lines, measurement indicators"

**Key Elements**:
- Person's back against wall
- One arm extended as if drawing a bow
- Measuring tape from wall to nocking point on face
- Clear measurement line with dimensions

### 3. Draw Length Arrow Method
**Prompt**: "Technical illustration of special draw length arrow with measurement markings, being drawn on a bow, clean instructional style, measurement scale visible"

**Key Elements**:
- Specialized arrow with measurement markings
- Bow at full draw position
- Clear view of measurement scale on arrow
- Indication of where to read the measurement

### 4. Professional Measurement Setup
**Prompt**: "Clean technical diagram of archery shop measurement setup with draw board, measuring stick, professional equipment, instructional manual style"

**Key Elements**:
- Draw board or measurement device
- Professional measuring equipment
- Clean, organized shop environment
- Clear measurement indicators

---

## Bow Weight Selection Guide Illustrations

### 1. Draw Weight Testing Illustration
**Prompt**: "Technical illustration showing proper form for testing bow draw weight, person drawing bow to full draw, clean instructional style, side view, form indicators"

**Key Elements**:
- Person demonstrating proper draw form
- Bow at full draw position
- Form indicators (straight back, proper anchor)
- Weight measurement indicator

### 2. Age-Based Weight Chart
**Prompt**: "Clean infographic showing recommended draw weights by age groups, bar chart style, professional design, green color scheme"

**Key Elements**:
- Age ranges on x-axis (8-12, 13-16, 17-20, Adult)
- Weight ranges on y-axis
- Clear, readable bars
- Professional chart styling

### 3. Bow Weight Progression
**Prompt**: "Technical diagram showing bow weight adjustment mechanism, limb bolts and adjustment points, exploded view style, clean technical illustration"

**Key Elements**:
- Compound bow limb and cam system
- Adjustment bolts clearly marked
- Direction arrows showing adjustment
- Clear labeling of components

---

## Sight Setup & Tuning Guide Illustrations

### 1. Sight Types Comparison
**Prompt**: "Technical diagram showing different bow sight types side by side - single pin, multi-pin, target sight, pendulum sight, clean comparison layout"

**Key Elements**:
- Four different sight types clearly shown
- Each sight labeled with key features
- Clean, comparative layout
- Technical drawing style

### 2. Sight Installation Steps
**Prompt**: "Step-by-step technical illustration showing bow sight installation process, exploded view of mounting hardware, instructional manual style"

**Key Elements**:
- Bow riser with mounting holes
- Sight bracket and hardware
- Step-by-step assembly process
- Clear component labeling

### 3. Pin Alignment Diagram
**Prompt**: "Technical diagram showing proper sight pin alignment and spacing, measurement indicators, clean instructional style, precision setup"

**Key Elements**:
- Multiple sight pins properly spaced
- Measurement indicators between pins
- Alignment references
- Distance labels (20yd, 30yd, etc.)

### 4. Sight Picture Examples
**Prompt**: "Clean diagram showing correct sight picture through bow sight aperture, pin placement, target alignment, instructional style"

**Key Elements**:
- Circular sight aperture view
- Properly centered pin
- Target in background
- Alignment indicators

---

## Grip & Stance Guide Illustrations

### 1. Proper Stance Comparison
**Prompt**: "Technical illustration comparing square stance vs open stance, overhead view and side view, clean instructional diagrams, foot positioning"

**Key Elements**:
- Two stance types side by side
- Foot position clearly marked
- Body alignment indicators
- Overhead and side view perspectives

### 2. Bow Grip Hand Position
**Prompt**: "Detailed technical illustration of proper bow grip, hand placement on bow handle, pressure points, side view and front view"

**Key Elements**:
- Hand properly positioned on bow grip
- Pressure point indicators
- Thumb and finger positioning
- Multiple viewing angles

### 3. Body Alignment Diagram
**Prompt**: "Technical diagram showing proper archery body alignment, skeleton/bone structure visible, T-formation shoulders, clean instructional style"

**Key Elements**:
- Skeletal alignment visible
- Shoulder line perpendicular to target
- Spine alignment
- Balance indicators

### 4. Common Mistakes Examples
**Prompt**: "Instructional diagram showing correct vs incorrect grip and stance positions, red X marks for wrong technique, green checkmarks for correct"

**Key Elements**:
- Side-by-side comparison
- Clear right/wrong indicators
- Common mistake examples
- Corrective guidance arrows

---

## General Technical Elements

### Measurement Indicators
- Double-headed arrows for distances
- Dimension lines with clear measurements
- Angle indicators where needed
- Scale references

### Color Coding
- **Blue**: Draw length guide elements
- **Green**: Bow weight guide elements  
- **Purple**: Sight setup guide elements
- **Orange**: Grip & stance guide elements
- **Red**: Incorrect techniques/warnings
- **Green checkmarks**: Correct techniques

### Typography
- Clean, sans-serif fonts
- Clear hierarchy (titles, labels, measurements)
- High contrast for readability
- Consistent sizing throughout

---

## Implementation Suggestions

### Option 1: AI Image Generation
Use the prompts above with:
- DALL-E 3
- Midjourney
- Stable Diffusion
- Adobe Firefly

### Option 2: Vector Illustrations
Create clean SVG illustrations using:
- Adobe Illustrator
- Inkscape (free)
- Figma
- Canva Pro

### Option 3: Photography + Overlays
- Take reference photos
- Add technical overlays
- Include measurement indicators
- Apply consistent styling

### Option 4: Existing Resources
- Search for royalty-free archery instruction images
- Modify existing technical diagrams
- Use educational archery resources with proper licensing

---

## File Organization

Suggested file structure:
```
frontend/assets/images/guides/
├── draw-length/
│   ├── wingspan-method.svg
│   ├── wall-method.svg
│   ├── arrow-method.svg
│   └── professional-setup.svg
├── bow-weight/
│   ├── weight-testing.svg
│   ├── age-chart.svg
│   └── weight-progression.svg
├── sight-setup/
│   ├── sight-types.svg
│   ├── installation.svg
│   ├── pin-alignment.svg
│   └── sight-picture.svg
└── grip-stance/
    ├── stance-comparison.svg
    ├── grip-position.svg
    ├── body-alignment.svg
    └── common-mistakes.svg
```

---

## Integration with Guides

Once illustrations are created, they can be integrated into the Vue components using:

```vue
<div class="illustration-container mb-6">
  <img 
    src="/images/guides/draw-length/wingspan-method.svg" 
    alt="Wingspan method for measuring draw length"
    class="w-full max-w-lg mx-auto rounded-lg shadow-sm"
  />
  <p class="text-sm text-gray-600 dark:text-gray-400 text-center mt-2">
    Wingspan Method: Measure fingertip to fingertip, then divide by 2.5
  </p>
</div>
```

This would significantly enhance the educational value and professional appearance of the guides.