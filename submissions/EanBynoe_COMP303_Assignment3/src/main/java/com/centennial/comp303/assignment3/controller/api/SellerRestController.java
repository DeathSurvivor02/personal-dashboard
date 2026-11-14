package com.centennial.comp303.assignment3.controller.api;

import com.centennial.comp303.assignment3.model.Seller;
import com.centennial.comp303.assignment3.service.SellerService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/sellers")
public class SellerRestController {

    private final SellerService sellerService;

    public SellerRestController(SellerService sellerService) {
        this.sellerService = sellerService;
    }

    @GetMapping
    public Flux<Seller> getAllSellers() {
        return sellerService.getAllSellers();
    }

    @GetMapping("/{sellerId}")
    public Mono<Seller> getSellerById(@PathVariable Long sellerId) {
        return sellerService.getSellerById(sellerId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Mono<Seller> createSeller(@Valid @RequestBody Seller seller) {
        return sellerService.createSeller(seller);
    }

    @PutMapping("/{sellerId}")
    public Mono<Seller> updateSeller(@PathVariable Long sellerId, @Valid @RequestBody Seller seller) {
        return sellerService.updateSeller(sellerId, seller);
    }

    @DeleteMapping("/{sellerId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> deleteSeller(@PathVariable Long sellerId) {
        return sellerService.deleteSeller(sellerId);
    }
}
