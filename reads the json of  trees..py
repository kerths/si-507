#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json

def read_tree_from_json(filename):

    with open(filename, 'r') as file:
        tree = json.load(file)
    return tree

def print_tree(node, indent=""):

    if isinstance(node, dict):
        for key, val in node.items():
            print(indent + str(key))
            print_tree(val, indent + "    ")
    elif isinstance(node, list):
        for val in node:
            print(indent + "- " + str(val))
    else:
        print(indent + "Data: " + str(node))

def main():
    filename = 'restaurant_tree.json'
    tree = read_tree_from_json(filename)
    print_tree(tree)

if __name__ == "__main__":
    main()


# In[ ]:




