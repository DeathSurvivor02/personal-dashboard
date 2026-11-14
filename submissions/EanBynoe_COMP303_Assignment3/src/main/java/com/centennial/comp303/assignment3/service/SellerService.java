package com.centennial.comp303.assignment3.service;

import com.centennial.comp303.assignment3.exception.ResourceNotFoundException;
import com.centennial.comp303.assignment3.model.Seller;
import com.centennial.comp303.assignment3.repository.ReactiveSellerRepository;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class SellerService {

    private final ReactiveSellerRepository sellerRepository;

    public SellerService(ReactiveSellerRepository sellerRepository) {
        this.sellerRepository = sellerRepository;
    }

    public Flux<Seller> getAllSellers() {
        return sellerRepository.findAll();
    }

    public Mono<Seller> getSellerById(Long sellerId) {
        return sellerRepository.findBySellerId(sellerId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Seller not found with ID: " + sellerId)));
    }

    public Mono<Seller> createSeller(Seller seller) {
        return sellerRepository.existsBySellerId(seller.getSellerId())
                .flatMap(exists -> {
                    if (Boolean.TRUE.equals(exists)) {
                        return Mono.error(new IllegalArgumentException("Seller ID already exists: " + seller.getSellerId()));
                    }
                    return sellerRepository.save(seller);
                });
    }

    public Mono<Seller> updateSeller(Long sellerId, Seller updated) {
        return sellerRepository.findBySellerId(sellerId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Seller not found with ID: " + sellerId)))
                .flatMap(existing -> {
                    existing.setSellerName(updated.getSellerName());
                    existing.setEmail(updated.getEmail());
                    existing.setBusinessType(updated.getBusinessType());
                    existing.setCity(updated.getCity());
                    existing.setRating(updated.getRating());
                    return sellerRepository.save(existing);
                });
    }

    public Mono<Void> deleteSeller(Long sellerId) {
        return sellerRepository.findBySellerId(sellerId)
                .switchIfEmpty(Mono.error(new ResourceNotFoundException("Seller not found with ID: " + sellerId)))
                .flatMap(existing -> sellerRepository.deleteBySellerId(sellerId));
    }
}
