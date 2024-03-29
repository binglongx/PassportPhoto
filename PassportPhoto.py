# Passport Photo Cropper V0.4
# (c)2023-2024, Binglong X.
# Move and zoom a photo against a template to crop for passport requirements.

from PIL import Image, ImageTk  # may need `pip install Pillow`
import requests                 # may need `pip install requests`
import tkinter as tk
from tkinter import filedialog as fd
import io
import webbrowser
#import argparse

# You can define a template class that must expose width, height, name, and draw()
# width and height can be in any units. Cropper will calculate proper scaling using them when calling draw().

# China Passport/Visa
# http://us.china-embassy.gov.cn/lsfw/zj/hzlxz/201903/t20190309_5098803.htm
class PhotoTemplate_ChinaPassport:
    ### public
    name = "China Passport/Visa";
    unit = "mm";
    width = 33;     #
    height = 48;    #
    instructions = "Zoom and scale photo so the head is between the small and bigger solid boxes.";
    illustrationURL = "http://losangeles.china-consulate.gov.cn/chn/lbqw/lszj/hzlxz/202401/W020240103256802928407.jpg";
    url = "http://losangeles.china-consulate.gov.cn/chn/lbqw/lszj/hzlxz/202401/t20240103_11216138.htm";

    ### private {{{
    # internal structure of template from (0,0) == top left: all in `unit`
    head_top_min = 3;   # 
    head_top_max = 5;   # 
    head_top = 5;         # 
    face_width_min = 15;  # excluding ear
    face_width_max = 22;  # excluding ear
    head_height_min = 28; # top to chin
    head_height_max = 33; # top to chin
    chin_bottom = 7;
    ### }}}

    @staticmethod
    def describe():
        t = PhotoTemplate_ChinaPassport;
        units = " " + t.unit;
        description = "Photo width: " + str(t.width) + units + ", height: " + str(t.height) + units + ". \n";
        description += "Face width (excluding hair/ear): " + str(t.face_width_min) + " to " + str(t.face_width_max) + units + ". \n";
        description += "Head height (top of hair to bottom of chin): " + str(t.head_height_min) + " to " + str(t.head_height_max) + units + ". \n";
        description += "Top of hair to top border: " + str(t.head_top_min) + " to " + str(t.head_top_max) + units + ". This template uses " + str(t.head_top) + units + ". \n";
        description += "Bottom of chin to bottom border: at least " + str(t.chin_bottom) + units + " (not shown / already met in this template).";
        return description;

    # draw template in canvas.
    # center of template is drawn at (x,y) in canvas, in pixels
    # scaling == actual_width_drawn_in_canvas / self.width, in pixels/mm in this template
    # hideTemplateGuts: whether you hide guts (so only border is drawn)
    @staticmethod 
    def draw(canvas, x, y, scaling, hideTemplateGuts):
        t = PhotoTemplate_ChinaPassport;
        width = t.width;
        height = t.height;
        s = scaling;

        #### border
        lw = 2;
        bw = t.width * s;
        bh = t.height * s;
        canvas.create_rectangle(x - bw / 2 - lw, y - bh / 2 - lw, x + bw / 2 + lw, y + bh / 2 + lw, outline='red', width=lw, dash=(5,2));
        if hideTemplateGuts:
            return; # do not draw further
        
        #### head/face box
        ytop = y - bh / 2 + t.head_top * s;
        ybottom_max = ytop + t.head_height_max * s;
        ybottom_min = ytop + t.head_height_min * s;
        face_width_s_min = t.face_width_min * s;
        face_width_s_max = t.face_width_max * s;
        ## outer box
        canvas.create_rectangle(x - face_width_s_max / 2, ytop, x + face_width_s_max / 2, ybottom_max, outline='green', width=1);
        ## inner box
        canvas.create_rectangle(x - face_width_s_min / 2, ytop, x + face_width_s_min / 2, ybottom_min, outline='green', width=1);

# USA Passport/Visa
class PhotoTemplate_USAPassport:
    ### public
    name = "USA Passport/Visa";
    unit = "inches";
    width = 2;     #
    height = 2;    #
    instructions = "Zoom and scale photo so the head height is between the short and long guide lines in the right half; then move photo so eye level is at the guide line in the left half.";
    illustrationURL = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos/photo-composition-template/_jcr_content/tsg-rwd-content-page-parsysxxx/image.img.jpg/1595428938021.jpg";
    url = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos/photo-composition-template.html";
    
    ### private {{{, all in `unit`
    eye_height_min = 1 + 1.0/8;
    eye_height_max = 1 + 3.0/8;
    eye_height = (eye_height_min + eye_height_max) / 2;
    head_height_min = 1;
    head_height_max = 1 + 3.0/8;
    ### }}} 
    
    @staticmethod
    def describe():
        t = PhotoTemplate_USAPassport;
        units = " " + t.unit;
        description = "Photo width: " + str(t.width) + units + ", height: " + str(t.height) + units + ". \n";
        description += "Head height (top of hair to bottom of chin): " + str(t.head_height_min) + " to " + str(t.head_height_max) + units + ". \n";
        description += "Eye height: " + str(t.eye_height_min) + " to " + str(t.eye_height_max) + units + ". This template uses " + str(t.eye_height) + units + ".";
        return description;

    # draw template in canvas.
    # center of template is drawn at (x,y) in canvas, in pixels
    # scaling == actual_width_drawn_in_canvas / self.width, in pixels/mm in this template
    # hideTemplateGuts: whether you hide guts (so only border is drawn)
    @staticmethod 
    def draw(canvas, x, y, scaling, hideTemplateGuts):
        t = PhotoTemplate_USAPassport;
        width = t.width;
        height = t.height;
        s = scaling;

        #### border
        lw = 2;
        bw = t.width * s;
        bh = t.height * s;
        canvas.create_rectangle(x - bw / 2 - lw, y - bh / 2 - lw, x + bw / 2 + lw, y + bh / 2 + lw, outline='red', width=lw, dash=(5,2));
        if hideTemplateGuts:
            return; # do not draw further

        #### vertical line
        canvas.create_line(x, y-bh/2, x, y+bh/2, width = 1, dash = (2, 2))

        #### eye level
        eye_y = y + bh/2 - t.eye_height*s;
        canvas.create_line(x, eye_y, x-bw/2, eye_y, width = 1, fill='red');

        ### head height
        head_center = eye_y;
        ## max
        hh_max = t.head_height_max * s;
        canvas.create_line(x, head_center - hh_max/2, x+bw/2, head_center - hh_max/2, width = 2, fill='green');
        canvas.create_line(x, head_center + hh_max/2, x+bw/2, head_center + hh_max/2, width = 2, fill='green');
        ## min
        hh_min = t.head_height_min * s;
        canvas.create_line(x, head_center - hh_min/2, x+bw/2*0.75, head_center - hh_min/2, width = 1, fill='green');
        canvas.create_line(x, head_center + hh_min/2, x+bw/2*0.75, head_center + hh_min/2, width = 1, fill='green');



# Manage zoom and move of photo
class PassportCropper:
    def __init__(self, templateClass, canvas, originalImage, hidingTemplateGuts):
        self.templateClass = templateClass;
        self.canvas = canvas;
        self.originalImage = originalImage;
        self.offsetX = 0;
        self.offsetY = 0;
        
        self.scalingMax = 3;
        self.scalingMin = 0.1;
        
        self.scaling = 1;
        self.translation = (0, 0);
        self.transientTranslation = (0, 0);
        self.isDown = False;
        self.hidingTemplateGuts = hidingTemplateGuts;
        
        """Activate / deactivate mousewheel scrolling when 
        cursor is over / not over the widget respectively."""
        canvas.bind("<Enter>", lambda _: canvas.bind_all('<MouseWheel>', self.onMouseWheel));
        canvas.bind("<Leave>", lambda _: canvas.unbind_all('<MouseWheel>'));
        
        canvas.bind("<Button-1>", self.onMouseButton1Down);
        canvas.bind("<ButtonRelease-1>", self.onMouseButton1Up);
        canvas.bind('<Motion>', self.onMouseMove)
        #self.redraw();
    
    def setHideTemplateGuts(self, hiding):
        if self.hidingTemplateGuts != hiding:
            self.hidingTemplateGuts = hiding;
            self.redraw();
    
    def setOriginalImage(self, original):
        self.originalImage = original;
        self.redraw();
    
    def onTransientMove(self, transientTranslation):
        # print("onTransientMove: delta x: ", transientTranslation[0], " y: ", transientTranslation[1]);
        self.transientTranslation = transientTranslation;
        self.redraw();
    
    def onMouseButton1Down(self, event):
        self.isDown = True;
        self.downXY = (event.x, event.y);
        self.transientTranslation = (0, 0);
        print("onMouseButton1Down: event x: ", event.x, " y: ", event.y);
    
    def onMouseMove(self, event):
        # print("onMouseMove: event x: ", event.x, " y: ", event.y);
        if self.isDown:
            self.onTransientMove(( event.x - self.downXY[0], event.y - self.downXY[1]) )
    
    def onMouseButton1Up(self, event):
        print("onMouseButton1Up: event x: ", event.x, " y: ", event.y);
        if self.isDown:
            transientTranslation = ( event.x - self.downXY[0], event.y - self.downXY[1]);
            self.isDown = False;            
            self.translation = (self.translation[0] + transientTranslation[0], self.translation[1] + transientTranslation[1]);
            self.transientTranslation = (0, 0);
            self.redraw();
    
    def onScaling(self, s):
        self.scaling = max(min(self.scaling * s, self.scalingMax), self.scalingMin);
        print("onScaling: scaling: ", self.scaling);
        self.redraw();
    
    def onMouseWheel(self, event):
        minimal_s = 0.02;
        d = event.delta;
        if d > 0 :
            s = (minimal_s * d) + 1.0;
        else:
            s = 1.0 / ( (minimal_s * -d) + 1.0 );
        self.onScaling(s);
    
    def transformImage(self):
        sz = self.originalImage.size;
        # self.transformedImage = self.originalImage;
        self.transformedImage = self.originalImage.resize((int(sz[0] * self.scaling), int(sz[1] * self.scaling)), Image.Resampling.LANCZOS);
        # print('transformImage: original:', sz, " new:", self.transformedImage.size);
    
    def redraw(self):
        self.canvas.delete("all");
        self.transformImage();
        self.drawImage();
        self.drawTemplate();
        self.canvas.update();
    
    def drawImage(self):
        # print('drawImage: ');
        self.tempImage = ImageTk.PhotoImage(self.transformedImage);
        self.canvas.create_image(self.translation[0]+self.transientTranslation[0], self.translation[1]+self.transientTranslation[1], image=self.tempImage, anchor='nw');
    
    def drawTemplate(self):
        w = self.canvas.winfo_width();
        h = self.canvas.winfo_height();
        # leave some buffer at edges
        ww = w * 0.9;
        hh = h * 0.9;

        sz = self.originalImage.size;
        sx = ww / self.templateClass.width;
        sy = hh / self.templateClass.height;
        s = min(sx, sy);
        self.templateClass.draw(self.canvas, w/2, h/2, s, self.hidingTemplateGuts);

def runPhotoCropper(templateClass, windowWidth, windowHeight):
    window = tk.Tk()
    
    # window.geometry("2000x1400");
    window.geometry(str(windowWidth)+"x"+str(windowHeight));
    # window.title("Passport Photo Cropper (China)");
    window.title("Photo Cropper: " + templateClass.name)
    
    canvas = tk.Canvas(window, width=windowWidth-400, height=windowHeight-90, bg='black')
    canvas.grid(row = 0, column = 0, rowspan = 7, sticky = tk.W, padx = 5, pady = 5);
    
    # originalImage = Image.open("photo.jpg");
    originalImage = Image.new(mode="RGB", size=(800, 800)); # placeholder
    cropper = PassportCropper(templateClass, canvas, originalImage, False);

    # Load button
    def selectFile():
        filetypes = ( ('All files', '*.*') );
        filename = fd.askopenfilename( title='Open an image file', initialdir='/' );
        original = Image.open(filename);
        cropper.setOriginalImage(original);
    
    buttonLoad = tk.Button(window, text = "Load Photo ...", command=selectFile);
    buttonLoad.grid(row = 0, column = 1, sticky = tk.W, pady = 2);
    
    # Hide checkbox
    chkHideTemplateGuts_Variable = tk.BooleanVar(False);
    def chkHideTemplateGuts_Update():
        cropper.setHideTemplateGuts(chkHideTemplateGuts_Variable.get());
    chkHideTemplateGuts = tk.Checkbutton(window, text = "Hide Template Internals", onvalue=True, offvalue=False, \
                                        variable=chkHideTemplateGuts_Variable, \
                                        command=chkHideTemplateGuts_Update);
    chkHideTemplateGuts.grid(row = 1, column = 1, sticky = tk.W, pady = 2);
    
    # Instructions
    instructions = tk.Message(window, width=380, text = templateClass.instructions);
    instructions.grid(row = 2, column = 1, sticky = tk.W, pady = 2);

    # Help message
    help = tk.Message(window, width=380, text = "Usage: Click and drag to move photo; scroll to zoom photo. When matching template well, hide the template internals, and screen capture the template box (excluding border). This is the photo you need.");
    help.grid(row = 3, column = 1, sticky = tk.W, pady = 2);

    # Requirements description
    requirements = tk.Message(window, width=380, text = "Photo Requirements: \n\n" + templateClass.describe() + " \n\nSee link below");
    requirements.grid(row = 4, column = 1, sticky = tk.W, pady = 2);

    # Website 
    def callback(url):
        webbrowser.open_new_tab(url)
    link = tk.Label(window, text=templateClass.url, fg="lightblue", cursor="hand")
    link.grid(row = 5, column = 1, sticky = tk.W, pady = 2);
    link.bind("<Button-1>", lambda e: callback(templateClass.url))

    # Illustration image
    img_loaded = False
    try:
        illustrationImage = requests.get(templateClass.illustrationURL, allow_redirects=True);
        if illustrationImage.status_code == 200: # good
            img = ImageTk.PhotoImage(Image.open(io.BytesIO(illustrationImage.content)))
            illustration = tk.Label(window, image=img)
            img_loaded = True
    except Exception:
        pass
    if not img_loaded:
        illustration = tk.Message(window, width=380, text = "Cannot load illustration image: \n" + templateClass.illustrationURL + " \nPlease go to the URL above to check.");
    illustration.grid(row = 6, column = 1, sticky = tk.W, pady = 2);

    cropper.redraw()
    window.mainloop()


def chooseCountry():
    dialog = tk.Tk()
    dialog.geometry("300x200")
    dialog.title("Choose country");
    choice = tk.StringVar(dialog, "China")
    
    def onOK():
        dialog.destroy()
    
    #tk.Radiobutton(dialog, text = "China", variable = choice, value = "China", indicator = 0, background = "light blue").pack(fill = tk.X, ipady = 5)
    tk.Label(dialog, text="Choose country to crop passport photo for:", ).pack(fill=tk.X, ipady=20)
    tk.Radiobutton(dialog, text="China", variable=choice, value="China", indicator=0).pack(fill=tk.X, ipady=5)
    tk.Radiobutton(dialog, text = "USA", variable = choice, value = "USA", indicator = 0).pack(fill = tk.X, ipady = 5)
    
    tk.Button(dialog, text= "OK", font=("Calibri",14,"bold"), command=onOK).pack(pady=20)
    
    dialog.mainloop()
    return choice.get()

# main() starts here:

#country = chooseCountry()
country = "China" # or "USA"

if country == "China":
    runPhotoCropper(PhotoTemplate_ChinaPassport, 1800, 1250)
elif country == "USA":
    runPhotoCropper(PhotoTemplate_USAPassport, 1900, 1250);
else:
    print("Unknown country: " + country)

#runPhotoCropper(PhotoTemplate_ChinaPassport, 1800, 1250);
#runPhotoCropper(PhotoTemplate_USAPassport, 1900, 1250);
