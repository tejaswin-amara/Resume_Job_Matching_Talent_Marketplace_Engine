package com.talentengine.service;

import java.io.InputStream;

public interface StorageService {
    void store(String filename, InputStream content);
    void init();
}
