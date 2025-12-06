import customtkinter as ctk
from gui.sign_up_window import SignUpWindow
from gui.manager_window import ManagerWindow
from gui.college_window import CollegeWindow
from gui.courier_window import CourierWindow

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")


class KSUInventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # - Basic Window Setup-
        self.title("KSU Inventory Management System")
        self.geometry("1000x600")

        # Configure grid for resizing (important for responsive UI)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Frame Container ---
        # This container holds all other windows (Pages)
        self.frame_container = ctk.CTkFrame(self)
        self.frame_container.grid(row=0, column=0, sticky="nsew")
        self.frame_container.grid_rowconfigure(0, weight=1)
        self.frame_container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Start the application on the Sign Up/Login page
        self.show_frame("SignUpWindow")

    def show_frame(self, page_name, user_id=None):
        """
        Switches the currently displayed frame/window.
        (Requirement: Navigating from one window to another should be easy and clear)
        """

        # Lazy loading: Create the frame only when requested
        if page_name not in self.frames:

            # --- Import and Instantiate the new window based on page_name (Required for forwarding) ---
            if page_name == "SignUpWindow":

                frame = SignUpWindow(master=self.frame_container, controller=self)

            elif page_name == "ManagerWindow":

                frame = ManagerWindow(master=self.frame_container, controller=self)

            elif page_name == "CollegeWindow":

                frame = CollegeWindow(master=self.frame_container, controller=self)

            elif page_name == "CourierWindow":

                frame = CourierWindow(master=self.frame_container, controller=self)

            else:
                # Fallback for unknown pages
                raise ValueError(f"Application Error: Unknown page name '{page_name}' requested.")

            self.frames[page_name] = frame

        frame = self.frames[page_name]

        # Pass the authenticated user's ID to the destination frame
        if user_id:
            frame.user_id = user_id

        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()  # Brings the newly requested frame to the front

        # Optional: Set the window title to reflect the current page
        self.title(f"KSU Inventory Management System - {page_name.replace('Window', '')}")


if __name__ == "__main__":
    app = KSUInventoryApp()
    app.mainloop()