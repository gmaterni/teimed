#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__date__ = "29-07-2021"
__version__ = "0.3.1"
__author__ = "Marta Materni"

prj = {
    "witness_checkover": {
        "log": "0",
        "exe": [
            [
                "checkover.py",
                "-i witness/witness.txt",
                "-c teimcfg/teimoverflow.csv"
            ]
        ]
    },
    "witness_checktxt": {
        "log": "0",
        "exe": [
            [
                "checktxt.py",
                "-i witness/witness.txt"
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
                "-t teimcfg/teimtags.csv"
            ]
        ]

    },
    "witness_setid": {
        "log": "0",
        "exe": [
            [
                "teimsetid.py ",
                "-i witness/witness.txt",
                "-t teimcfg/teimxmlid.csv"
            ]
        ]
    },
    "witness_over": {
        "log": "0",
        "exe": [
            [
                "teimover.py ",
                "-i witness/witness.txt",
                "-c teimcfg/teimoverflow.csv"
            ]
        ]
    },
    "witness_note": {
        "log": "0",
        "exe": [
            [
                "teimnote.py ",
                "-i witness/witness.txt",
                "-n witness/teimnote.csv"
            ]
        ],
        "include": {
            "host": "teimcfg/tei.xml",
            "dest": "xml/witness.xml",
            "params": [],
            "files": [
                "XML_MANO|witness/log/witness_id_over_note.xml"
            ]
        }
    },
    "witness_format": {
        "log": "0",
        "exe": [
            [
                "teimxmlformat.py",
                "-i witness/log/witness_id_over_note.xml",
                "-o witness/witness_f.xml",
                "-a"
            ]
        ]
    },
    "witness": {
        "log": "0",
        "exe": [
            "prjmgr.py prj/witness_removelog.json",
            "prjmgr.py prj/witness_merge.json",
            "prjmgr.py prj/witness_txt.json",
            "prjmgr.py prj/witness_setid.json",
            "prjmgr.py prj/witness_over.json",
            "prjmgr.py prj/witness_note.json",
            "prjmgr.py prj/witness_format.json"
        ]
    }
}

###############################

prj_witness = {
    "text_checkover": {
        "log": "0",
        "exe": [
            [
                "checkover.py",
                "-i witness/text.txt",
                "-c teimcfg/teimoverflow.csv"
            ]
        ]
    },
    "text_checktxt": {
        "log": "0",
        "exe": [
            [
                "checktxt.py",
                "-i witness/text.txt"
            ]
        ]
    },
    "text_format": {
        "log": "0",
        "exe.1": [
            [
                "teimxmlformat.py",
                "-i witness/log/text_id_over_note.xml",
                "-o witness/text.xml",
                "-a"
            ]
        ]
    },
    "text": {
        "log": "0",
        "exe": [
            "prjmgr.py prj_witness/text_txt.json",
            "prjmgr.py prj_witness/text_setid.json",
            "prjmgr.py prj_witness/text_over.json",
            "prjmgr.py prj_witness/text_note.json",
            "prjmgr.py prj_witness/text_format.json"
        ]
    },
    "text_setid": {
        "log": "0",
        "exe": [
            [
                "teimsetid.py",
                "-i witness/text.txt",
                "-t teimcfg/teimxmlid.csv"
            ]
        ]
    },
    "text_note": {
        "log": "0",
        "exe": [
            [
                "teimnote.py",
                "-i witness/text.txt",
                "-n witness/teimnote.csv"
            ]
        ]
    },
    "text_over": {
        "log": "0",
        "exe": [
            [
                "teimover.py",
                "-i witness/text.txt",
                "-c teimcfg/teimoverflow.csv"
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
                "-t teimcfg/teimtags.csv"
            ]
        ]
    }
}
