# Pi Cloud Server

A personal local cloud storage system built with Raspberry Pi.

---

## ⚠️ Prototype Notice

> **This repository contains a prototype implementation built for demonstration and submission purposes. The current version is developed and tested on a standard computer. Final deployment and hardware integration with Raspberry Pi will be performed after receiving approval from Blueprint Hack Club.**

---

## Project Overview

This project demonstrates a self-hosted cloud storage concept using:

- **Flask** backend with REST API
- **PostgreSQL** database for file metadata
- **Raspberry Pi** as target deployment platform

The goal is to create a personal alternative to commercial cloud storage services.

---

## Repository Contents

| Folder                                 | Description                         |
| -------------------------------------- | ----------------------------------- |
| `pi-cloud-server/`                     | Backend server (Flask + PostgreSQL) |
| `CAD/`                                 | 3D enclosure designs                |
| `PCB & SHEMANTIC FOR EXTERNALL BOARD/` | Custom PCB for Pi expansion         |

---

## Hardware Design

### PCB Design

<img width="1247" height="973" alt="PCB" src="https://github.com/user-attachments/assets/5278bfda-9c32-47a3-af0d-71c7a102c26c" />

Custom expansion board providing additional ports and cooling support.

### CAD Enclosure

3D-printable enclosure with:

- Front/back removable panels
- SSD mounting slot
- Port cutouts for Pi and expansion board

---

## Quick Start

```bash
cd pi-cloud-server
pip install -r requirements.txt
python app.py
```

See `pi-cloud-server/README.md` for detailed instructions.

---

## Future Plans (Post-Grant Approval)

- Raspberry Pi 4 deployment
- External SSD integration
- Full file upload/download
- Web dashboard
- User authentication

---

## Contact

Email: mjlabishek123@gmail.com

---

## License

MIT License

---

_Built for Blueprint Hack Club_
