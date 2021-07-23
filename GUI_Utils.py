import tkinter as tk


def frame_create(parent, text_, row_, col_, colspan_, rowspan_):                        # Creates a frame and puts it on the grid
    aux_frame = tk.LabelFrame(parent, text=text_)                                       # Create frame widget
    aux_frame.grid(row=row_, column=col_, columnspan=colspan_, rowspan=rowspan_)        # Put it on the specified row and column
    return aux_frame


def entry_create(parent, width_, row_, col_, pad_x, pad_y, label, var: tk.DoubleVar):   # Creates a Label on the right and an Entry to the left
    aux_label = tk.Label(parent, text=label, width=width_, padx=pad_x, pady=pad_y)      # Create Label widget first
    aux_label.grid(row=row_, column=col_-1)                                             # Put it in column 0 of the frame
    aux_entry = tk.Entry(parent, width=width_, textvar=var)                             # Create Entry widget
    aux_entry.grid(row=row_, column=col_, padx=pad_x, pady=pad_y)                       # Put Entry in the row and column specified
    var.set(0)                                                                          # Initialize variable
    return aux_label, aux_entry


def spinbox_create(parent, width_, row_, col_, pad_x, pad_y, label, var: tk.IntVar):    # Creates a Label on the right and an Entry to the left
    aux_label = tk.Label(parent, text=label, width=width_, padx=pad_x, pady=pad_y)      # Create Label widget first
    aux_label.grid(row=row_, column=col_ - 1)                                           # Put it in column 0 of the frame
    aux_spinbox = tk.Spinbox(parent, width=width_, textvar=var, from_=0, to=10000, increment=1, state='readonly') # Create Spinbox widget
    aux_spinbox.grid(row=row_, column=col_, padx=pad_x, pady=pad_y)                     # Put Spinbox in the row and column specified
    var.set(0)                                                                          # Initialize variable
    return aux_label, aux_spinbox


def label_create(parent, width_, row_, col_, pad_x, pad_y, label, var: tk.StringVar):   # Creates two labels on the same row
    aux_label1 = tk.Label(parent, text=label, width=width_, padx=pad_x, pady=pad_y)     # Create Label widget
    aux_label1.grid(row=row_, column=col_-1)                                            # Put it in column 0 of the frame
    aux_label2 = tk.Label(parent, textvariable=var, width=width_, padx=pad_x, pady=pad_y)  # Create Label widget
    aux_label2.grid(row=row_, column=col_)                                              # Put it in column 1 of the frame
    # var.set('0')                                                                        # Initialize variable
    return aux_label2
