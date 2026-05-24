import streamlit as st
from rembg import remove
from PIL import Image, ImageOps
import io

# Page Config - Responsive Layout for Mobile and Laptop
st.set_page_config(
    page_title="PixlAI Studio - Ultimate Image Editor", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(45deg, #00EFB2, #0078FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #0078FF, #00EFB2) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        border: none !important;
        width: 100%;
        box-shadow: 0px 4px 10px rgba(0, 120, 255, 0.2);
    }
    .stButton>button:hover {
        box-shadow: 0px 6px 20px rgba(0, 239, 178, 0.4);
        transform: scale(1.01);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>⚡ BG-Zap & Resize Studio</h1>", unsafe_allow_html=True)
st.write("Responsive AI Image Processor for Mobile and Desktop Browsers.")
#Enter your desired description here:
st.write("Direct Background Remover & Custom Image Resizer.")
# Sidebar Controls
st.sidebar.header("🛠️ Studio Control Panel")

# Main File Input
uploaded_file = st.sidebar.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load original image
    input_image = Image.open(uploaded_file).convert("RGBA")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI Background Control")
    
    # 1. BG Remove Toggle
    remove_bg = st.sidebar.toggle("Remove Background", value=True)
    
    # 2. BG Change Options (Visible only when background is removed)
    bg_mode = "Transparent (PNG)"
    bg_color = "#FFFFFF"
    custom_bg_file = None
    
    if remove_bg:
        bg_mode = st.sidebar.selectbox(
            "Select New Background", 
            ["Transparent (PNG)", "Solid Color (Passport/ID)", "Custom Background Image"]
        )
        
        if bg_mode == "Solid Color (Passport/ID)":
            bg_color = st.sidebar.color_picker("Pick Background Color", "#FFFFFF")
            
        elif bg_mode == "Custom Background Image":
            custom_bg_file = st.sidebar.file_uploader("Upload New BG Image", type=["jpg", "jpeg", "png"], key="bg_img")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📐 Image Resizing")
    
    # 3. Resize Inputs
    resize_option = st.sidebar.checkbox("Apply Custom Size")
    width = input_image.width
    height = input_image.height
    
    if resize_option:
        col_w, col_h = st.sidebar.columns(2)
        with col_w:
            width = st.number_input("Width (px)", value=input_image.width, step=1)
        with col_h:
            height = st.number_input("Height (px)", value=input_image.height, step=1)

    # 4. Extra Pro Tools
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Quick Transforms")
    rotate_angle = st.sidebar.slider("Rotate Image", 0, 360, 0, step=90)

    # Layout Setup - Automatically adapts to Mobile screens
    main_col1, main_col2 = st.columns([1, 1])
    
    with main_col1:
        st.subheader("🖼️ Input Preview")
        st.image(uploaded_file, use_container_width=True, caption=f"Original: {input_image.width}x{input_image.height} px")
        
    with main_col2:
        st.subheader("✨ PixlAI Processed Result")
        
        with st.spinner("AI Processing... Please wait..."):
            
            # Base Layer Setup
            processed_image = input_image
            
            # Action 1: Remove Background
            if remove_bg:
                img_byte_arr = io.BytesIO()
                input_image.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # AI BG Removal
                no_bg_bytes = remove(img_bytes)
                no_bg_img = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
                
                # Action 2: Background Changing Logic
                if bg_mode == "Transparent (PNG)":
                    processed_image = no_bg_img
                    
                elif bg_mode == "Solid Color (Passport/ID)":
                    # Create a solid color background layer
                    background = Image.new("RGBA", no_bg_img.size, bg_color)
                    # Composite the images together
                    processed_image = Image.alpha_composite(background, no_bg_img)
                    
                elif bg_mode == "Custom Background Image" and custom_bg_file is not None:
                    custom_bg = Image.open(custom_bg_file).convert("RGBA")
                    # Match custom background size with the foreground image
                    custom_bg = custom_bg.resize(no_bg_img.size, Image.Resampling.LANCZOS)
                    processed_image = Image.alpha_composite(custom_bg, no_bg_img)
                    
            # Action 3: Rotations
            if rotate_angle != 0:
                processed_image = processed_image.rotate(rotate_angle, expand=True)
                
            # Action 4: Resizing
            if resize_option:
                processed_image = processed_image.resize((int(width), int(height)), Image.Resampling.LANCZOS)
            
            # Display Final Image
            final_display = processed_image.convert("RGB") if bg_mode != "Transparent (PNG)" else processed_image
            st.image(final_display, use_container_width=True, caption=f"Output: {processed_image.width}x{processed_image.height} px")
            
            # Action 5: Safe Buffer for Downloading
            buffer = io.BytesIO()
            processed_image.save(buffer, format="PNG")
            byte_im = buffer.getvalue()
            
            st.markdown("---")
            # Safe and clean download button for both Mobile & PC Chrome
            st.download_button(
                label="📥 Download High-Quality PNG",
                data=byte_im,
                file_name="PixlAI_Studio_Output.png",
                mime="image/png"
            )
            st.balloons()
else:
    # Home screen layout
    st.info("👈 Please upload an image from the left control panel to get started!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📱 100% Mobile Responsive")
        st.write("Open this application on your Mobile Chrome browser. It dynamically rescales to fit your screen perfectly, and the download button saves files straight to your phone gallery.")
    with col2:
        st.markdown("### 🎨 Smart BG Changer")
        st.write("Instantly apply standard white/blue solid backdrops for passport/ID photos, or let e-commerce sellers swap backgrounds with premium digital showrooms.")