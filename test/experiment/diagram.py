import streamlit as st
import re
import uuid
import streamlit.components.v1 as components

# --- EXAMPLE USAGE ---
response = """
## Hello! Here is the project plan you asked for. 

First, we have the initialization phase:
```mermaid
flowchart TD
  A[Start] --> B{Decision}
  B -->|Option A| C[Process A]
  B -->|Option B| D[Process B]
  C --> E[End]
  D --> E
```
```mermaid
gantt
    title A Computing Project
    section Phase 1
    Research :a1, 2023-01-01, 30d
    Design   :after a1, 20d
```

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
```
"""

# -------- RENDER MERMAID AND MARKDOWN ------
num_lines = len(response.split('\n'))
dynamic_height = max(300, min(num_lines * 20, 800)) 

def render_mermaid(code: str, height: int = 400):
    unique_id = f"mermaid-{uuid.uuid4().hex[:8]}"
    
    html_code = f"""
    <div id="container-{unique_id}" style="position: relative; border: 1px solid #ddd; border-radius: 8px; width: 100%; height: {height}px; background: white;">
        <button onclick="downloadPNG('{unique_id}')" style="
            position: absolute; top: 10px; right: 10px; z-index: 1000;
            padding: 5px 12px; cursor: pointer; background: #ffffff;
            border: 1px solid #dcdfe6; border-radius: 4px; font-size: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: sans-serif;">
            🖼️ Download PNG
        </button>
        
        <div id="{unique_id}" class="mermaid" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
            {code}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
        mermaid.initialize({{ 
            startOnLoad: false, 
            theme: 'default',
            securityLevel: 'loose'
        }});

        async function render() {{
            const element = document.getElementById("{unique_id}");
            try {{
                const {{ svg }} = await mermaid.render('svg-{unique_id}', `{code}`);
                element.innerHTML = svg;

                const svgElement = element.querySelector('svg');
                svgElement.setAttribute('width', '100%');
                svgElement.setAttribute('height', '100%');
                
                window.panZoom = svgPanZoom(svgElement, {{
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true
                }});
            }} catch (e) {{
                element.innerHTML = "<p style='color:red'>Mermaid Error: " + e.message + "</p>";
            }}
        }}
        render();

        window.downloadPNG = function(id) {{
            const svgElement = document.querySelector(`#${{id}} svg`);
            if (!svgElement) return alert("Diagram not ready");

            // 1. GANTT FIX: Temporarily remove '100%' width to measure real content size
            const originalWidth = svgElement.style.width;
            svgElement.style.width = 'auto'; 
            svgElement.setAttribute('width', 'auto');

            // 2. Hide navigation controls for a clean export
            const controls = svgElement.querySelector('.svg-pan-zoom-control');
            if(controls) controls.style.display = 'none';

            const bbox = svgElement.getBBox();
            const padding = 20; 
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const scale = 3; // High-res for clear text

            canvas.width = (bbox.width + padding * 2) * scale;
            canvas.height = (bbox.height + padding * 2) * scale;
            
            const originalViewBox = svgElement.getAttribute("viewBox");
            svgElement.setAttribute("viewBox", `${{bbox.x}} ${{bbox.y}} ${{bbox.width}} ${{bbox.height}}`);
            
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const img = new Image();
            const encodedData = window.btoa(unescape(encodeURIComponent(svgData)));
            img.src = "data:image/svg+xml;base64," + encodedData;

            img.onload = function() {{
                ctx.scale(scale, scale);
                ctx.drawImage(img, padding, padding, bbox.width, bbox.height);
                
                const pngUrl = canvas.toDataURL("image/png");
                const downloadLink = document.createElement("a");
                downloadLink.href = pngUrl;
                downloadLink.download = "mermaid-diagram.png";
                downloadLink.click();
                
                // 3. Restore UI state for the browser
                svgElement.setAttribute("viewBox", originalViewBox);
                svgElement.style.width = originalWidth;
                if(controls) controls.style.display = 'block';
            }};
        }};
    </script>
    """
    components.html(html_code, height=height + 20)

# -------- UPDATED HYBRID PARSER ----------
def render_hybrid_response(text: str):
    parts = re.split(r'(```mermaid\n.*?\n```)', text, flags=re.DOTALL)
    
    for part in parts:
        if part.startswith("```mermaid"):
            clean_code = part.replace("```mermaid\n", "").replace("```", "").strip()
            
            # AUTO-HEIGHT DETECTION
            # Gantt charts need more vertical space than flowcharts
            if clean_code.lower().startswith("gantt") or "classDiagram" in clean_code:
                custom_height = 600
            else:
                custom_height = 400
                
            render_mermaid(clean_code, height=custom_height)
        else:
            st.markdown(part)

# def render_mermaid(code: str, height: int = 400):
#     unique_id = f"mermaid-{uuid.uuid4().hex[:8]}"
    
#     # We set width: 100% on the container and the internal div
#     html_code = f"""
#     <div id="container-{unique_id}" style="border: 1px solid #ddd; border-radius: 8px; width: 100%; height: {height}px; background: white;">
#         <div id="{unique_id}" class="mermaid" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
#             {code}
#         </div>
#     </div>

#     <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
#     <script type="module">
#         import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        
#         // Initialize with useMaxWidth: false so we can control it manually
#         mermaid.initialize({{ 
#             startOnLoad: false, 
#             theme: 'default',
#             securityLevel: 'loose',
#         }});

#         const renderDiagram = async () => {{
#             const element = document.getElementById("{unique_id}");
#             const graphDefinition = `{code}`;
            
#             // Render the diagram
#             const {{ svg }} = await mermaid.render('svg-{unique_id}', graphDefinition);
#             element.innerHTML = svg;

#             const svgElement = element.querySelector('svg');
            
#             // --- THE FIX: Remove Mermaid's hardcoded dimensions ---
#             svgElement.style.width = '100%';
#             svgElement.style.height = '100%';
#             svgElement.style.maxWidth = '100%';
#             svgElement.removeAttribute('height'); 
            
#             // Initialize Pan & Zoom
#             window.panZoom = svgPanZoom(svgElement, {{
#                 zoomEnabled: true,
#                 controlIconsEnabled: true,
#                 fit: true,
#                 center: true,
#                 minZoom: 0.1,
#                 maxZoom: 10
#             }});
#         }};

#         renderDiagram();
#     </script>
#     """
#     # Use use_container_width logic or set width to None to fill the Streamlit column
#     components.html(html_code, height=height + 20)

# def render_hybrid_response(text: str):
#     # Regex to find mermaid blocks: ```mermaid ... ```
#     parts = re.split(r'(```mermaid\n.*?\n```)', text, flags=re.DOTALL)
    
#     for part in parts:
#         if part.startswith("```mermaid"):
#             # Strip the backticks and 'mermaid' keyword to get raw code
#             clean_code = part.replace("```mermaid\n", "").replace("```", "")
#             render_mermaid(clean_code)
#         else:
#             # It's just regular markdown
#             st.markdown(part)

# Usage
st.title("Custom Mermaid.js Renderer")

render_hybrid_response(response)