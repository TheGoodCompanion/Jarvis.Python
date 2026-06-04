from assistant import JarvisAssistant
from gui.app import JarvisGui
import threading

def main():
    assistant = JarvisAssistant()
    gui = JarvisGui()

    assistant.on_status_changed = gui.queue_status
    assistant.on_transcript = gui.queue_transcipt
    assistant.on_response = gui.queue_response
    assistant.on_context_changed = gui.queue_context

    assistant_thread = threading.Thread(target=assistant.run, daemon=True)
    assistant_thread.start()
    gui.run()

if __name__ == "__main__":
    main()