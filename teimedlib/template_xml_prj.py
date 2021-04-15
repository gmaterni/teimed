#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__date__ = "01-03-2021"
__version__ = "0.1.2"
__author__ = "Marta Materni"

prj = {
    "witness_checkover": {
        "log": "0",
        "exe": [
            [
                "checkover.py",
                "-i witness/witness.txt",
                "-c cfg/overflow.csv",
                "-o witness/log/witness_checkover.log"
            ]
        ]
    },
    "witness_checktxt": {
        "log": "0",
        "exe": [
            [
                "checktxt.py",
                "-i witness/witness.txt",
                "-o witness/log/witness_checktxt.log"
            ]
        ]
    },
    "witness_merge": {
        "log": "0",
        "remove_dir": [
            {
                "dir": "witness",
                "pattern": "witness.txt"
            }
        ],
        "merge_dir": {
            "dir": "witness",
            "pattern": "*.txt",
            "out_path": "witness/witness.txt"
        }
    },
    "witness_removelog": {
        "log": "0",
        "remove_dir": [
            {
                "dir": "witness",
                "pattern": "witness.*"
            },
            {
                "dir": "witness",
                "pattern": "witness_format.*"
            },
            {
                "dir": "witness",
                "pattern": "*.log"
            },
            {
                "dir": "witness/log",
                "pattern": "*.*"
            }
        ]

    },
    "witness_txt": {
        "log": "0",
        "exe": [
            [
                "teimxml.py ",
                "-i witness/witness.txt",
                "-t cfg/teimedlib.csv",
                "-o witness/log/witness_teim.txt"
            ]
        ]

    },
    "witness_xml": {
        "log": "0",
        "exe": [
            [
                "teimsetid.py",
                "-i witness/log/witness_teim.txt",
                "-o witness/log/witness_id.xml",
                "-s G -n 'pb:1,cb:1,lg:1,l:1'"
            ],
            [
                "teimover.py",
                "-i witness/log/witness_id.xml",
                "-o witness/log/witness_id_over.xml",
                "-c cfg/overflow.csv"
            ],
            [
                "teimnote.py",
                "-i witness/log/witness_id_over.xml",
                "-o witness/log/witness_id_over_note.xml",
                "-n witness/note.csv"
            ]
        ],
        "include": {
            "host": "cfg/tei.xml",
            "dest": "xml/witness.xml",
            "params": [],
            "files": [
                "XML_MANO|witness/log/witness_id_over_note.xml"
            ]
        },
        "exe.1": [
            [
                "teimxmllint.py",
                "-i xml/witness.xml",
                "-o witness/witness_format.xml "
            ]
        ]
    },
    "witness": {
        "log": "0",
        "exe": [
            "prjmgr.py prj/witness_removelog.json",
            "prjmgr.py prj/witness_merge.json",
            "prjmgr.py prj/witness_txt.json",
            "prjmgr.py prj/witness_xml.json"
        ]
    }
}
###############################
witness_prj = {
    "text_checkover": {
        "log": "0",
        "exe": [
            [
                "checkover.py",
                "-i witness/text.txt",
                "-c cfg/overflow.csv",
                "-o witness/log/text_checkover.log"
            ]
        ]
    },
    "text_checktxt": {
        "log": "0",
        "exe": [
            [
                "checktxt.py",
                "-i witness/text.txt",
                "-o witness/log/text_checktxt.log"
            ]
        ]
    },
    "text_format": {
        "log": "0",
        "exe.1": [
            [
                "teimxmlformat.py",
                "-i witness/log/text_id_over_note.xml",
                "-o witness/text.xml "
            ]
        ]
    },
    "text": {
        "log": "0",
        "exe": [
            "prjmgr.py witness_prj/text_txt.json",
            "prjmgr.py witness_prj/text_setid.json",
            "prjmgr.py witness_prj/text_over.json",
            "prjmgr.py witness_prj/text_note.json",
            "prjmgr.py witness_prj/text_format.json"
        ]
    },
    "text_setid": {
        "log": "0",
        "exe": [
            [
                "teimsetid.py",
                "-i witness/log/text_teim.txt",
                "-o witness/log/text_id.xml",
                "-s G -n 'pb:1,cb:1,lg:1,l:1'"
            ]
        ]
    },
    "text_note": {
        "log": "0",
        "exe": [
            [
                "teimnote.py",
                "-i witness/log/text_id_over.xml",
                "-o witness/log/text_id_over_note.xml",
                "-n witness/note.csv"
            ]
        ]
    },
    "text_over": {
        "log": "0",
        "exe": [
            [
                "teimover.py",
                "-i witness/log/text_id.xml",
                "-o witness/log/text_id_over.xml",
                "-c cfg/overflow.csv"
            ]
        ]
    },
    "text_removelog": {
        "log": "0",
        "remove_dir": [
            {
                "dir": "witness",
                "pattern": "text.xml"
            },
            {
                "dir": "witness",
                "pattern": "text_format.xml"
            },
            {
                "dir": "witness/log",
                "pattern": "*.*"
            }
        ]
    },
    "text_txt": {
        "log": "0",
        "exe": [
            [
                "teimxml.py ",
                "-i witness/text.txt",
                "-t cfg/teimedlib.csv",
                "-o witness/log/text_teim.txt"
            ]
        ]
    }
}
