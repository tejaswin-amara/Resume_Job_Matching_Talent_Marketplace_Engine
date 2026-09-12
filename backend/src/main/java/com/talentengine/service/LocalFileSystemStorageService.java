package com.talentengine.service;

import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

@Service
public class LocalFileSystemStorageService implements StorageService {

    private final Path rootLocation;

    public LocalFileSystemStorageService() {
        this.rootLocation = Paths.get("upload-dir");
    }

    @Override
    @PostConstruct
    public void init() {
        try {
            Files.createDirectories(rootLocation);
        }
        catch (IOException e) {
            throw new RuntimeException("Could not initialize storage", e);
        }
    }

    @Override
    public void store(String filename, InputStream content) {
        try {
            if (filename == null || filename.isEmpty()) {
                throw new RuntimeException("Failed to store file with empty name.");
            }
            Path destinationFile = this.rootLocation.resolve(Paths.get(filename))
                    .normalize().toAbsolutePath();
            if (!destinationFile.getParent().equals(this.rootLocation.toAbsolutePath())) {
                throw new RuntimeException("Cannot store file outside current directory.");
            }
            Files.copy(content, destinationFile, StandardCopyOption.REPLACE_EXISTING);
        }
        catch (IOException e) {
            throw new RuntimeException("Failed to store file.", e);
        }
    }
}
