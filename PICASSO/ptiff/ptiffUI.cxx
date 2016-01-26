// generated by Fast Light User Interface Designer (fluid) version 1.0106

#include "ptiffUI.h"

inline void ptiffUI::cb_range__i(Fl_Value_Slider* o, void*) {
  if (display_->value() != 0) {
  display_->color_scale((int)((Fl_Slider *)o)->value(),(int)((Fl_Slider *)offset_)->value(),1);
};
}
void ptiffUI::cb_range_(Fl_Value_Slider* o, void* v) {
  ((ptiffUI*)(o->parent()->user_data()))->cb_range__i(o,v);
}

inline void ptiffUI::cb_offset__i(Fl_Value_Slider* o, void*) {
  if (display_->value() != 0) {
  display_->color_scale((int)((Fl_Slider *)range_)->value(),(int)((Fl_Slider *)o)->value(),1);
};
}
void ptiffUI::cb_offset_(Fl_Value_Slider* o, void* v) {
  ((ptiffUI*)(o->parent()->user_data()))->cb_offset__i(o,v);
}

inline void ptiffUI::cb_openfile__i(Fl_Button*, void*) {
  Fl_File_Chooser *fc = new Fl_File_Chooser(".","*.tif,*.png,*.jpg",Fl_File_Chooser::SINGLE,"Open Image");
fc->preview(0);
fc->color((Fl_Color)23);
fc->show();

while(fc->shown())
  Fl::wait();

if (fc->value() == NULL) return;

char *filename = (char *)fc->value();

if ((filename[strlen(filename)-3] != 't') && (filename[strlen(filename)-3] != 'T')) {
  range_->deactivate();
  offset_->deactivate();
} else {
  range_->activate();
  offset_->activate();
}

Ifl = Fl_Shared_Image::get(filename);

filename_->value(filename);
display_->value(Ifl);
display_->color_scale((int)((Fl_Slider *)range_)->value(),(int)((Fl_Slider *)offset_)->value(),1);
Fl_Image_Display::set_gamma(1.4);
}
void ptiffUI::cb_openfile_(Fl_Button* o, void* v) {
  ((ptiffUI*)(o->parent()->user_data()))->cb_openfile__i(o,v);
}

inline void ptiffUI::cb_previous__i(Fl_Button*, void*) {
  char *filename = (char *)filename_->value();
filenamestep(filename,-1);
if (!fexist(filename)) {
  filenamestep(filename,1);
  return;
}
if ((filename[strlen(filename)-3] != 't') && (filename[strlen(filename)-3] != 'T')) {
  range_->deactivate();
  offset_->deactivate();
} else {
  range_->activate();
  offset_->activate();
}

Ifl = Fl_Shared_Image::get(filename);

display_->value(Ifl);
display_->color_scale((int)((Fl_Slider *)range_)->value(),(int)((Fl_Slider *)offset_)->value(),1);
filename_->value(filename);
filename_->redraw();

Fl_Image_Display::set_gamma(1.4);
}
void ptiffUI::cb_previous_(Fl_Button* o, void* v) {
  ((ptiffUI*)(o->parent()->user_data()))->cb_previous__i(o,v);
}

inline void ptiffUI::cb_next__i(Fl_Button*, void*) {
  char *filename = (char *)filename_->value();
filenamestep(filename,1);

if (!fexist(filename)) {
  filenamestep(filename,-1);
  return;
}

if ((filename[strlen(filename)-3] != 't') && (filename[strlen(filename)-3] != 'T')) {
  range_->deactivate();
  offset_->deactivate();
} else {
  range_->activate();
  offset_->activate();
}
Ifl = Fl_Shared_Image::get(filename);
display_->value(Ifl);
display_->color_scale((int)((Fl_Slider *)range_)->value(),(int)((Fl_Slider *)offset_)->value(),1);
filename_->value(filename);
filename_->redraw();

Fl_Image_Display::set_gamma(1.4);
}
void ptiffUI::cb_next_(Fl_Button* o, void* v) {
  ((ptiffUI*)(o->parent()->user_data()))->cb_next__i(o,v);
}

ptiffUI::ptiffUI() {
  Fl_Double_Window* w;
  { Fl_Double_Window* o = window_ = new Fl_Double_Window(555, 435, "PICASSO Image Viewer");
    w = o;
    o->user_data((void*)(this));
    { Fl_Image_Display* o = display_ = new Fl_Image_Display(0, 35, 555, 310);
      o->box(FL_DOWN_BOX);
      o->color(FL_BACKGROUND_COLOR);
      o->selection_color(FL_BACKGROUND_COLOR);
      o->labeltype(FL_NORMAL_LABEL);
      o->labelfont(0);
      o->labelsize(14);
      o->labelcolor(FL_BLACK);
      o->align(FL_ALIGN_TOP);
      o->when(FL_WHEN_RELEASE);
      o->end();
      Fl_Group::current()->resizable(o);
    }
    { Fl_Output* o = filename_ = new Fl_Output(65, 350, 490, 25, "Filename");
      o->color((Fl_Color)23);
      o->when(FL_WHEN_CHANGED);
    }
    { Fl_Value_Slider* o = range_ = new Fl_Value_Slider(48, 380, 507, 25, "Range");
      o->tooltip("Set image interpolation range");
      o->type(5);
      o->color((Fl_Color)23);
      o->maximum(65535);
      o->step(1);
      o->value(4096);
      o->callback((Fl_Callback*)cb_range_);
      o->align(FL_ALIGN_LEFT);
    }
    { Fl_Value_Slider* o = offset_ = new Fl_Value_Slider(48, 408, 507, 25, "Offset");
      o->tooltip("Set image interpolation offset");
      o->type(5);
      o->color((Fl_Color)23);
      o->maximum(4096);
      o->step(1);
      o->callback((Fl_Callback*)cb_offset_);
      o->align(FL_ALIGN_LEFT);
    }
    { Fl_Button* o = openfile_ = new Fl_Button(0, 5, 55, 25, "Open");
      o->callback((Fl_Callback*)cb_openfile_);
    }
    { Fl_Button* o = previous_ = new Fl_Button(65, 5, 40, 25, "<");
      o->callback((Fl_Callback*)cb_previous_);
    }
    { Fl_Button* o = next_ = new Fl_Button(115, 5, 40, 25, ">");
      o->callback((Fl_Callback*)cb_next_);
    }
    o->end();
  }
}

ptiffUI::~ptiffUI() {
  delete window_;
}

void ptiffUI::show() {
}