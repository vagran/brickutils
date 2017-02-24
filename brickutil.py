#!/usr/bin/env python3
import configparser
import json
import os
import argparse
import re
import urllib.request
import urllib.parse


from io import TextIOWrapper

progArgs = None
config = None

globalParams = {
    "brickowl": {
        "apiUrl": "https://api.brickowl.com/v1"
    }
}

defaultConfig = {
    "brickowl": {
        "key": None
    }
}


def LoadConfig():
    global config

    path = os.path.join(os.path.expanduser("~"), ".brickutil.conf")
    if os.path.exists(path):
        config = configparser.ConfigParser()
        config.read(path)
    else:
        config = defaultConfig


def WishlistRemoveColors(srcWlId, dstWlId):
    listUrl = "%s/wishlist/lots?key=%s&wishlist_id=%s" % (globalParams["brickowl"]["apiUrl"],
                                                          config["brickowl"]["key"],
                                                          srcWlId)

    with urllib.request.urlopen(listUrl) as f:
        lots = json.load(TextIOWrapper(f))
    print("%d lots to process" % len(lots))

    createUrl = "%s/wishlist/create_lot" % globalParams["brickowl"]["apiUrl"]
    updateUrl = "%s/wishlist/update" % globalParams["brickowl"]["apiUrl"]
    boidRe = re.compile("(\\d+)\\-\\d+")
    for lot in lots:
        boid = lot["boid"]
        m = boidRe.match(boid)
        if m is not None:
            boid = m.group(1)
        print("Lot %s BOID %s" % (lot["lot_id"], boid))

        data = urllib.parse.urlencode({
            "key": config["brickowl"]["key"],
            "wishlist_id": dstWlId,
            "boid": boid
        }).encode("utf-8")
        with urllib.request.urlopen(createUrl, data = data) as f:
            resp = json.load(TextIOWrapper(f))
            if resp["status"] != "Success":
                raise Exception("Failed to create lot: " + str(resp))

        data = urllib.parse.urlencode({
            "key": config["brickowl"]["key"],
            "wishlist_id": dstWlId,
            "lot_id": resp["lot_id"],
            "minimum_quantity": lot["qty"]
        }).encode("utf-8")
        with urllib.request.urlopen(updateUrl, data = data) as f:
            resp = json.load(TextIOWrapper(f))
            if resp["status"] != "Success":
                raise Exception("Failed to update lot: " + str(resp))

    print("%d lots added to destination wishlist" % len(lots))


def ListWishlists():
    url = "%s/wishlist/lists?key=%s" % (globalParams["brickowl"]["apiUrl"],
                                        config["brickowl"]["key"])
    with urllib.request.urlopen(url) as f:
        list = json.load(TextIOWrapper(f))
    for wl in list:
        print("%s:\n\tID: %s\n\tsize: %s items in %s lots\n" %
              (wl["name"], wl["wishlist_id"], wl["item_count"], wl["lot_count"]))


def DumpWishlist(wlId):
    listUrl = "%s/wishlist/lots?key=%s&wishlist_id=%s" % (globalParams["brickowl"]["apiUrl"],
                                                          config["brickowl"]["key"],
                                                          wlId)

    with urllib.request.urlopen(listUrl) as f:
        lots = json.load(TextIOWrapper(f))
    #XXX
    print(lots)


def ExportBricklink(wlId, outPath):
    listUrl = "%s/wishlist/lots?key=%s&wishlist_id=%s" % (globalParams["brickowl"]["apiUrl"],
                                                          config["brickowl"]["key"],
                                                          wlId)

    with urllib.request.urlopen(listUrl) as f:
        lots = json.load(TextIOWrapper(f))

    with open(outPath, "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n")
        f.write("<INVENTORY>\n")
        for lot in lots:
            designId = None
            for _id in lot["ids"]:
                if _id["type"] == "design_id":
                    designId = _id["id"]
            if designId is None:
                print("Design id not found for lot %s" % lot["lot_id"])
                continue
            f.write("<ITEM>\n")
            #XXX set all fields
            f.write("""
<ITEMTYPE>P</ITEMTYPE>
<ITEMID>%s</ITEMID>
<MAXPRICE>-1.0000</MAXPRICE>
<MINQTY>%s</MINQTY>
<CONDITION>N</CONDITION>
<NOTIFY>N</NOTIFY>
""" % (designId, lot["qty"]))

            f.write("</ITEM>\n")
        f.write("</INVENTORY>\n")


def Main():
    global progArgs

    parser = argparse.ArgumentParser()
    parser.add_argument("command", metavar = "COMMAND", type = str,
                        nargs = 1, help = "Input file with cameras dump")

    parser.add_argument("--wishlist-id", help = "Related wishlist ID")
    parser.add_argument("--dst-wishlist-id", help = "Destination wishlist ID")
    parser.add_argument("-o", type = str, help = "Output file path")

    progArgs = parser.parse_args()

    LoadConfig()

    if progArgs.command[0] == "wishlist-remove-colors":
        if progArgs.wishlist_id is None:
            raise Exception("Wishlist ID required")
        WishlistRemoveColors(progArgs.wishlist_id, progArgs.dst_wishlist_id)

    elif progArgs.command[0] == "list-wishlists":
        ListWishlists()

    elif progArgs.command[0] == "dump-wishlist":
        DumpWishlist(progArgs.wishlist_id)

    elif progArgs.command[0] == "export-bricklink":
        if progArgs.o is None:
            raise Exception("Output file path should be specified")
        ExportBricklink(progArgs.wishlist_id, progArgs.o)


if __name__ == "__main__":
    Main()
