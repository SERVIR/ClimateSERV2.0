#!/usr/bin/env bash

sudo systemctl start django; sudo systemctl enable django; sudo systemctl enable nginx; sudo systemctl start nginx;