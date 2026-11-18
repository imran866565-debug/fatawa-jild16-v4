#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 16 easy-Urdu tashreeh v4 chunks into jild-16.json.

Reads the 13 leaf chunk files listed in chunks-manifest-v4-jild16.json,
concatenates them in order 01 -> 13, derives start_page = min(pages)
where the field is absent, normalises page markers, validates, and
writes {"masail": [...]} to jild-16.json.

ORDER -- chunk order is the order:
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-16.json
  has ID order == concatenation order of the v4 leaf chunks (verified
  locally by the coordinator: all 269 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.
  CHUNK_ORDER is the numeric range pattern 01-13.

NO JOINS in this merge: no masala spans two leaves as separate parts.
  The 8 boundary folds are written ONCE inside the earlier leaf,
  combining both halves' tashreeh into one flowing passage with ALL
  notes from both halves; the later leaf EXCLUDES the folded item:
  masala-46-48 (leaf 02, [142-145] -- folds in chunk-03's p145 half),
  masala-83-87 (leaf 04, [220-223] -- folds in chunk-05's masala-83
  [221-223]; chunk-04's own masala-83 [220] stays a SEPARATE item),
  masala-149 (leaf 06, [309-317] -- folds in chunk-07's [311-317] half),
  masala-211 (leaf 08, [420-422] -- folds in chunk-09's [421,422] half),
  masala-277 (leaf 09, [469-473] -- folds in chunk-10's p470 tail
  [471-473]), masala-319 (leaf 10, [515-522] -- folds in chunk-11's
  p521 tail [521,522]), masala-359 (leaf 11, [569-571] -- folds in
  chunk-12's [571] half), masala-428 (leaf 12, [614-625] -- folds in
  chunk-13's p625 tail [625]). Plain concatenation gives 269 items and
  269 unique ids. NO rename quirk in Jild 16's merge: the v3 merged
  file has 269 UNIQUE ids. Chunk present pages sum to exactly 542
  (= unique) -- no page is shared between any two chunk files.
  masala-185 (36 pages, jawab 57,874 chars) is the biggest single item
  in the jild; it sits whole in leaf 08, no split needed.

START_PAGE: every one of the 13 v4 leaf chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 13 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  269 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-16.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 542 unique pages (min 4, max 636);
  volume_ids == {52}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild16-pesh-lafz, last id jild16-khatima.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild16.json"

# Concatenation order: chunk files 01 -> 18, in order.
CHUNK_ORDER = [f"jild-16-chunk-{nn:02d}.json" for nn in range(1, 14)]

EXPECTED_ITEMS = 269
EXPECTED_PAGES = 542
EXPECTED_MIN_PAGE = 4
EXPECTED_MAX_PAGE = 636
EXPECTED_VOLUME_IDS = {52}
EXPECTED_FIRST_ID = "jild16-pesh-lafz"
EXPECTED_LAST_ID = "jild16-khatima"

# v3 ID sequence, verbatim from content/tashreeh/jild-16.json.
V3_IDS = ["jild16-pesh-lafz", "jild16-hamd", "jild16-masala-1", "jild16-masala-2", "jild16-masala-3", "jild16-masala-4-ta-10", "jild16-masala-11", "jild16-masala-12", "jild16-masala-13", "jild16-masala-14", "jild16-masala-15", "jild16-masala-16", "jild16-masala-17", "jild16-masala-18", "jild16-masala-19", "jild16-masala-20", "jild16-masala-21", "jild16-masala-22", "jild16-masala-23", "jild16-masala-24-28", "jild16-masala-29-33", "jild16-masala-34", "jild16-masala-35", "jild16-masala-36", "jild16-masala-37", "jild16-masala-38-41", "jild16-masala-42", "jild16-masala-43-45", "jild16-masala-46-48", "jild16-masala-49", "jild16-masala-50", "jild16-masala-51", "jild16-masala-52-53", "jild16-masala-54", "jild16-masala-55-56", "jild16-masala-57", "jild16-masala-58", "jild16-masala-59-60", "jild16-masala-61", "jild16-masala-62", "jild16-masala-63", "jild16-masala-64", "jild16-masala-65", "jild16-masala-66", "jild16-masala-67", "jild16-masala-68", "jild16-masala-69-73", "jild16-masala-74-75", "jild16-masala-76", "jild16-masala-77", "jild16-masala-78", "jild16-masala-79", "jild16-masala-80", "jild16-masala-81", "jild16-masala-83", "jild16-masala-83-87", "jild16-masala-88", "jild16-masala-92", "jild16-masala-93", "jild16-masala-103", "jild16-masala-106", "jild16-masala-107", "jild16-masala-108", "jild16-masala-114", "jild16-masala-120", "jild16-masala-122", "jild16-masala-123", "jild16-masala-124", "jild16-masala-125", "jild16-masala-126", "jild16-masala-127", "jild16-masala-128", "jild16-masala-129", "jild16-masala-131", "jild16-masala-132", "jild16-masala-133", "jild16-masala-134", "jild16-masala-135-136", "jild16-masala-137", "jild16-masala-138", "jild16-masala-139", "jild16-masala-140", "jild16-masala-141", "jild16-masala-142", "jild16-masala-143", "jild16-masala-144", "jild16-masala-145", "jild16-masala-146", "jild16-masala-147", "jild16-masala-148", "jild16-masala-149", "jild16-masala-150", "jild16-masala-151", "jild16-masala-152", "jild16-masala-153", "jild16-masala-154", "jild16-masala-155", "jild16-masala-156", "jild16-masala-157", "jild16-masala-158", "jild16-masala-159", "jild16-masala-160", "jild16-masala-161", "jild16-masala-162", "jild16-masala-163-165", "jild16-masala-166", "jild16-masala-167", "jild16-masala-168", "jild16-masala-169", "jild16-masala-170", "jild16-masala-171", "jild16-masala-172", "jild16-masala-173-181", "jild16-masala-182", "jild16-masala-183", "jild16-masala-184", "jild16-masala-185", "jild16-masala-186", "jild16-masala-187", "jild16-masala-190", "jild16-masala-194", "jild16-masala-196", "jild16-masala-197", "jild16-masala-198", "jild16-masala-202", "jild16-masala-204", "jild16-masala-205", "jild16-masala-207", "jild16-masala-208", "jild16-masala-210", "jild16-masala-211", "jild16-masala-213", "jild16-masala-216", "jild16-masala-217", "jild16-masala-220", "jild16-masala-221", "jild16-masala-222", "jild16-masala-223", "jild16-masala-226", "jild16-masala-227", "jild16-masala-228", "jild16-masala-229", "jild16-masala-230", "jild16-masala-231", "jild16-masala-234", "jild16-masala-235", "jild16-masala-242", "jild16-masala-244", "jild16-masala-245", "jild16-masala-246", "jild16-masala-247", "jild16-masala-251", "jild16-masala-254", "jild16-masala-255", "jild16-masala-257", "jild16-masala-258", "jild16-masala-259", "jild16-masala-260", "jild16-masala-261", "jild16-masala-263", "jild16-masala-264", "jild16-masala-265", "jild16-masala-266", "jild16-masala-272", "jild16-masala-273", "jild16-masala-274", "jild16-masala-275", "jild16-masala-276", "jild16-masala-277", "jild16-masala-278", "jild16-masala-279-280", "jild16-masala-281", "jild16-masala-282", "jild16-masala-283-284", "jild16-masala-285", "jild16-masala-286", "jild16-masala-287", "jild16-masala-288", "jild16-masala-289", "jild16-masala-290", "jild16-masala-291-292", "jild16-masala-293", "jild16-masala-294-296", "jild16-masala-297", "jild16-masala-298", "jild16-masala-299", "jild16-masala-300", "jild16-masala-301", "jild16-masala-302", "jild16-masala-303", "jild16-masala-304", "jild16-masala-305", "jild16-masala-306", "jild16-masala-307", "jild16-masala-308", "jild16-masala-309", "jild16-masala-310", "jild16-masala-311", "jild16-masala-312-313", "jild16-masala-314", "jild16-masala-315", "jild16-masala-316-318", "jild16-masala-319", "jild16-masala-320", "jild16-masala-321", "jild16-masala-322", "jild16-masala-323", "jild16-masala-325", "jild16-masala-326", "jild16-masala-327", "jild16-masala-329", "jild16-masala-330", "jild16-masala-331", "jild16-masala-332", "jild16-masala-333", "jild16-masala-334", "jild16-masala-335", "jild16-p539", "jild16-masala-338", "jild16-masala-339", "jild16-masala-340", "jild16-masala-341", "jild16-masala-345", "jild16-masala-346", "jild16-masala-348", "jild16-masala-349", "jild16-masala-350", "jild16-masala-351", "jild16-masala-352", "jild16-masala-353", "jild16-masala-354", "jild16-masala-355", "jild16-masala-357", "jild16-masala-358", "jild16-masala-359", "jild16-masala-360-365", "jild16-masala-366", "jild16-masala-367-374", "jild16-masala-375", "jild16-masala-376", "jild16-masala-377", "jild16-masala-378", "jild16-masala-379-381", "jild16-masala-382", "jild16-masala-383", "jild16-masala-384", "jild16-masala-385-388", "jild16-masala-389", "jild16-masala-390", "jild16-masala-391-398", "jild16-masala-399", "jild16-masala-400-403", "jild16-masala-404", "jild16-masala-405-408", "jild16-masala-409-410", "jild16-masala-611", "jild16-masala-412", "jild16-masala-413-416", "jild16-masala-417", "jild16-masala-418", "jild16-masala-419", "jild16-masala-420", "jild16-masala-421-427", "jild16-masala-428", "jild16-masala-429", "jild16-masala-430", "jild16-masala-431", "jild16-masala-432", "jild16-khatima"]

# v3 pages per item id, verbatim from content/tashreeh/jild-16.json.
V3_PAGES = {
"jild16-pesh-lafz": [4, 5, 6, 7, 9],
"jild16-hamd": [9],
"jild16-masala-1": [90],
"jild16-masala-2": [90, 91, 92, 93, 94],
"jild16-masala-3": [94, 95, 96],
"jild16-masala-4-ta-10": [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
"jild16-masala-11": [114, 115],
"jild16-masala-12": [115, 116],
"jild16-masala-13": [117],
"jild16-masala-14": [118],
"jild16-masala-15": [118, 119],
"jild16-masala-16": [119],
"jild16-masala-17": [119, 120, 121],
"jild16-masala-18": [121],
"jild16-masala-19": [121, 122],
"jild16-masala-20": [122, 123],
"jild16-masala-21": [123, 124],
"jild16-masala-22": [124],
"jild16-masala-23": [124],
"jild16-masala-24-28": [124, 125],
"jild16-masala-29-33": [125, 126, 127, 128, 129],
"jild16-masala-34": [129, 130],
"jild16-masala-35": [131, 132, 133, 134],
"jild16-masala-36": [135, 136],
"jild16-masala-37": [137],
"jild16-masala-38-41": [137, 138],
"jild16-masala-42": [139, 140],
"jild16-masala-43-45": [140, 141, 142],
"jild16-masala-46-48": [142, 143, 144, 145],
"jild16-masala-49": [146, 147, 148, 149, 150, 151],
"jild16-masala-50": [151],
"jild16-masala-51": [151],
"jild16-masala-52-53": [151, 152],
"jild16-masala-54": [152, 153, 154, 155, 156, 157],
"jild16-masala-55-56": [157, 158],
"jild16-masala-57": [158, 159],
"jild16-masala-58": [159],
"jild16-masala-59-60": [159, 160],
"jild16-masala-61": [160, 161, 162],
"jild16-masala-62": [162, 163, 164],
"jild16-masala-63": [164],
"jild16-masala-64": [164, 165],
"jild16-masala-65": [165, 166],
"jild16-masala-66": [166],
"jild16-masala-67": [166, 167, 168],
"jild16-masala-68": [168, 169, 170, 171, 172, 173, 174, 175],
"jild16-masala-69-73": [176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203],
"jild16-masala-74-75": [203, 204],
"jild16-masala-76": [206, 207],
"jild16-masala-77": [207, 208, 209],
"jild16-masala-78": [209, 210, 211, 212],
"jild16-masala-79": [213, 214, 215, 216],
"jild16-masala-80": [216, 217, 218, 219],
"jild16-masala-81": [219],
"jild16-masala-83": [220],
"jild16-masala-83-87": [220, 221, 222, 223],
"jild16-masala-88": [223, 224],
"jild16-masala-92": [224, 225],
"jild16-masala-93": [225, 226, 227, 228, 229, 230],
"jild16-masala-103": [230, 231],
"jild16-masala-106": [231, 232],
"jild16-masala-107": [232],
"jild16-masala-108": [232, 233, 234, 235],
"jild16-masala-114": [235, 236, 237, 238, 239, 240, 241, 242, 243],
"jild16-masala-120": [243],
"jild16-masala-122": [243, 244, 245],
"jild16-masala-123": [245, 246, 247, 248],
"jild16-masala-124": [249],
"jild16-masala-125": [249, 250, 251, 253],
"jild16-masala-126": [253],
"jild16-masala-127": [253, 254],
"jild16-masala-128": [254, 255],
"jild16-masala-129": [255],
"jild16-masala-131": [256, 258],
"jild16-masala-132": [258, 259, 260],
"jild16-masala-133": [260, 261],
"jild16-masala-134": [262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281],
"jild16-masala-135-136": [281, 282],
"jild16-masala-137": [282],
"jild16-masala-138": [282, 283, 284, 285],
"jild16-masala-139": [285, 286, 287, 288],
"jild16-masala-140": [288, 289],
"jild16-masala-141": [289, 290, 291, 292, 293],
"jild16-masala-142": [293, 294, 295],
"jild16-masala-143": [296, 297, 298],
"jild16-masala-144": [298, 299, 300],
"jild16-masala-145": [300],
"jild16-masala-146": [300, 301],
"jild16-masala-147": [301, 302, 303, 304, 305, 306, 307, 308],
"jild16-masala-148": [308, 309],
"jild16-masala-149": [309, 310, 311, 312, 313, 314, 315, 316, 317],
"jild16-masala-150": [317, 318],
"jild16-masala-151": [318, 319],
"jild16-masala-152": [319, 320],
"jild16-masala-153": [320, 321, 322, 323],
"jild16-masala-154": [323, 324],
"jild16-masala-155": [324, 325, 326, 327, 328, 329, 330, 331, 332, 333],
"jild16-masala-156": [333, 334],
"jild16-masala-157": [334],
"jild16-masala-158": [334, 335, 336],
"jild16-masala-159": [337, 338, 339, 340, 341],
"jild16-masala-160": [342],
"jild16-masala-161": [342, 343],
"jild16-masala-162": [343, 344],
"jild16-masala-163-165": [344, 345, 346, 347],
"jild16-masala-166": [348],
"jild16-masala-167": [348, 349],
"jild16-masala-168": [349, 350, 351],
"jild16-masala-169": [351, 352, 353, 354, 355],
"jild16-masala-170": [355],
"jild16-masala-171": [355, 356],
"jild16-masala-172": [356, 357, 358, 359],
"jild16-masala-173-181": [360, 362, 363],
"jild16-masala-182": [363, 364],
"jild16-masala-183": [364, 365],
"jild16-masala-184": [365],
"jild16-masala-185": [370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405],
"jild16-masala-186": [405, 406, 407],
"jild16-masala-187": [407],
"jild16-masala-190": [407, 408, 409, 410],
"jild16-masala-194": [410, 411],
"jild16-masala-196": [411],
"jild16-masala-197": [411, 412],
"jild16-masala-198": [412, 413],
"jild16-masala-202": [413, 414],
"jild16-masala-204": [414, 415],
"jild16-masala-205": [415, 416, 417, 418],
"jild16-masala-207": [418, 419],
"jild16-masala-208": [419, 420],
"jild16-masala-210": [420],
"jild16-masala-211": [420, 421, 422],
"jild16-masala-213": [422, 423],
"jild16-masala-216": [423, 424],
"jild16-masala-217": [424, 425],
"jild16-masala-220": [425, 426],
"jild16-masala-221": [426],
"jild16-masala-222": [426, 427, 428],
"jild16-masala-223": [428, 429],
"jild16-masala-226": [430],
"jild16-masala-227": [430],
"jild16-masala-228": [431],
"jild16-masala-229": [431, 432],
"jild16-masala-230": [432],
"jild16-masala-231": [432, 433],
"jild16-masala-234": [433, 434],
"jild16-masala-235": [434, 435, 436],
"jild16-masala-242": [436],
"jild16-masala-244": [436, 437, 438],
"jild16-masala-245": [438, 439],
"jild16-masala-246": [440],
"jild16-masala-247": [441, 442],
"jild16-masala-251": [442, 443, 444],
"jild16-masala-254": [444, 445],
"jild16-masala-255": [445],
"jild16-masala-257": [446],
"jild16-masala-258": [447, 448],
"jild16-masala-259": [448],
"jild16-masala-260": [448, 449],
"jild16-masala-261": [449, 450],
"jild16-masala-263": [450, 451],
"jild16-masala-264": [451, 452, 453],
"jild16-masala-265": [454],
"jild16-masala-266": [454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465],
"jild16-masala-272": [465, 466],
"jild16-masala-273": [466, 467],
"jild16-masala-274": [467, 468],
"jild16-masala-275": [468],
"jild16-masala-276": [468, 469],
"jild16-masala-277": [469, 470, 471, 472, 473],
"jild16-masala-278": [473],
"jild16-masala-279-280": [473, 474],
"jild16-masala-281": [475],
"jild16-masala-282": [475],
"jild16-masala-283-284": [475, 476, 477, 478, 479],
"jild16-masala-285": [479, 480, 481],
"jild16-masala-286": [481, 482, 483],
"jild16-masala-287": [483, 484, 485, 486],
"jild16-masala-288": [486, 487],
"jild16-masala-289": [488],
"jild16-masala-290": [488],
"jild16-masala-291-292": [489, 490, 491, 492],
"jild16-masala-293": [492, 493],
"jild16-masala-294-296": [493, 494],
"jild16-masala-297": [494, 495, 496, 497],
"jild16-masala-298": [498, 499],
"jild16-masala-299": [499, 500],
"jild16-masala-300": [500, 501],
"jild16-masala-301": [500, 501],
"jild16-masala-302": [501, 502],
"jild16-masala-303": [501, 502],
"jild16-masala-304": [502],
"jild16-masala-305": [502, 503, 504, 505],
"jild16-masala-306": [505, 506],
"jild16-masala-307": [506, 507],
"jild16-masala-308": [507, 508],
"jild16-masala-309": [509],
"jild16-masala-310": [509, 510],
"jild16-masala-311": [509, 510],
"jild16-masala-312-313": [511],
"jild16-masala-314": [511],
"jild16-masala-315": [511, 512, 513],
"jild16-masala-316-318": [513, 514, 515],
"jild16-masala-319": [515, 516, 517, 518, 519, 520, 521, 522],
"jild16-masala-320": [522],
"jild16-masala-321": [523, 524, 525],
"jild16-masala-322": [525, 526],
"jild16-masala-323": [526],
"jild16-masala-325": [527],
"jild16-masala-326": [527],
"jild16-masala-327": [528],
"jild16-masala-329": [528, 529],
"jild16-masala-330": [529, 530],
"jild16-masala-331": [530, 531, 532, 533, 534],
"jild16-masala-332": [534, 535],
"jild16-masala-333": [535, 536, 537],
"jild16-masala-334": [537, 538],
"jild16-masala-335": [538, 539],
"jild16-p539": [539, 540, 541, 542, 543],
"jild16-masala-338": [543, 544],
"jild16-masala-339": [544],
"jild16-masala-340": [544, 545],
"jild16-masala-341": [546, 547],
"jild16-masala-345": [547, 548],
"jild16-masala-346": [548, 549],
"jild16-masala-348": [549, 550],
"jild16-masala-349": [550, 551],
"jild16-masala-350": [551, 552],
"jild16-masala-351": [552, 553],
"jild16-masala-352": [553, 554],
"jild16-masala-353": [554, 555, 556, 557, 558, 559],
"jild16-masala-354": [559, 560],
"jild16-masala-355": [560, 561, 562, 563, 564, 565, 566, 567],
"jild16-masala-357": [567, 568],
"jild16-masala-358": [568, 569],
"jild16-masala-359": [569, 570, 571],
"jild16-masala-360-365": [571, 572, 573],
"jild16-masala-366": [574],
"jild16-masala-367-374": [574, 575, 576],
"jild16-masala-375": [577, 578],
"jild16-masala-376": [579],
"jild16-masala-377": [579],
"jild16-masala-378": [579],
"jild16-masala-379-381": [579, 580, 581, 582],
"jild16-masala-382": [582, 583],
"jild16-masala-383": [583, 584],
"jild16-masala-384": [584, 585],
"jild16-masala-385-388": [585, 586, 587],
"jild16-masala-389": [587],
"jild16-masala-390": [587, 588],
"jild16-masala-391-398": [588, 589],
"jild16-masala-399": [590],
"jild16-masala-400-403": [590, 591, 592],
"jild16-masala-404": [592],
"jild16-masala-405-408": [593, 594, 595],
"jild16-masala-409-410": [595, 596, 597, 598, 599, 600, 601, 602],
"jild16-masala-611": [602, 603, 604],
"jild16-masala-412": [604],
"jild16-masala-413-416": [604, 605],
"jild16-masala-417": [606, 607, 608],
"jild16-masala-418": [608],
"jild16-masala-419": [609, 610],
"jild16-masala-420": [610, 612],
"jild16-masala-421-427": [612, 613, 614],
"jild16-masala-428": [614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625],
"jild16-masala-429": [625, 626, 627],
"jild16-masala-430": [627, 628],
"jild16-masala-431": [628, 629, 630, 631, 632, 633, 634],
"jild16-masala-432": [634, 635, 636],
"jild16-khatima": [636],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 13, f"expected 13 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO JOINS in Jild 16: the 8 boundary folds (masala-46-48,
    # masala-83-87, masala-149, masala-211, masala-277, masala-319,
    # masala-359, masala-428) are written ONCE inside the earlier leaf,
    # combining both halves' tashreeh into one flowing passage with ALL
    # notes from both halves; the later leaf EXCLUDES the folded item.
    # No masala spans two leaves as separate parts, so plain
    # concatenation gives 269 items and 269 unique ids. No rename quirk
    # in Jild 16's merge: the v3 merged file has 269 UNIQUE ids.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS after concatenation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 16's merge; no joins)")

    print(f"concatenated: {len(all_items)} items (269 expected, no joins)")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-16.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-16.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
