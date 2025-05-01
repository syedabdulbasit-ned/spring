import threading
import time
import random


num_fruits = 50  
# tree = list(range(num_fruits)) 
tree = list(range(1, num_fruits + 1)) 
crate = []  
crate_lock = threading.Lock()  
tree_lock = threading.Lock()  
loader_event = threading.Event()  
loader_done = threading.Event()  
pickers_done = False 

def picker(id):
    global tree, pickers_done
    while True:
        with tree_lock:
            if not tree:
                print(f"Picker {id}: Tree is bare, exiting.")
                return
            fruit = tree.pop(0)
            print(f"Picker {id}: Picked fruit {fruit}.")
        
        with crate_lock:
            if len(crate) < 12:
                crate.append(fruit)
                print(f"Picker {id}: Placed fruit {fruit} in crate. Crate size: {len(crate)}.")
                if len(crate) == 12:
                    print(f"Picker {id}: Crate full, signaling loader.")
                    loader_event.set()
            else:
                # This case should theoretically never happen because we signal loader at 12
                print(f"Picker {id}: Crate full, waiting for loader.")
                loader_event.set()
                crate_lock.release()  # Release lock while waiting
                loader_done.wait()
                crate_lock.acquire()
                loader_done.clear()
                crate.append(fruit)
                print(f"Picker {id}: Placed fruit {fruit} in new crate. Crate size: {len(crate)}.")
        
        time.sleep(random.uniform(0.1, 0.3))

# def loader():
#     global crate, pickers_done
#     while True:
#         loader_event.wait()
#         with crate_lock:
#             if pickers_done and not crate:
#                 print("Loader: All pickers done and no fruits left, exiting.")
#                 return
#             if crate:
#                 print(f"Loader: Loading crate with {len(crate)} fruits to truck.")
#                 crate.clear()
#                 print("Loader: New empty crate provided.")
#             loader_event.clear()
#             loader_done.set()
#         time.sleep(random.uniform(0.2, 0.5))

def loader():
    global crate, pickers_done
    while not (pickers_done and not crate):  # Exit when pickers are done AND crate is empty
        loader_event.wait()
        with crate_lock:
            if not crate:
                continue  # Skip if crate is already empty
            print(f"Loader: Loading crate with {len(crate)} fruits to truck.")
            crate.clear()
            if not pickers_done:  # Only provide new crate if pickers are still active
                print("Loader: New empty crate provided.")
        loader_event.clear()
        loader_done.set()
    print("Loader: All work complete, exiting.")

def main():
    global pickers_done
    loader_done.set()
    loader_thread = threading.Thread(target=loader)
    loader_thread.start()
    
    pickers = [threading.Thread(target=picker, args=(i+1,)) for i in range(3)]
    for p in pickers:
        p.start()
    
    for p in pickers:
        p.join()
    
    with tree_lock:
        pickers_done = True
    
    loader_event.set()  # Signal loader for final crate
    loader_thread.join()
    print("Main: All operations completed.")

if __name__ == "__main__":
    main()
