package com.centennial.comp303.assignment3.controller.web;

import com.centennial.comp303.assignment3.model.CustomerOrder;
import com.centennial.comp303.assignment3.model.Product;
import com.centennial.comp303.assignment3.model.Seller;
import com.centennial.comp303.assignment3.service.CustomerOrderService;
import com.centennial.comp303.assignment3.service.ProductService;
import com.centennial.comp303.assignment3.service.SellerService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@Controller
public class MarketplaceWebController {

    private final SellerService sellerService;
    private final ProductService productService;
    private final CustomerOrderService orderService;

    public MarketplaceWebController(SellerService sellerService, ProductService productService, CustomerOrderService orderService) {
        this.sellerService = sellerService;
        this.productService = productService;
        this.orderService = orderService;
    }

    @GetMapping("/")
    public Mono<String> home(Model model) {
        return Mono.zip(
                sellerService.getAllSellers().collectList(),
                productService.getAllProducts().collectList(),
                orderService.getAllOrders().collectList()
        ).map(tuple -> {
            model.addAttribute("sellerCount", tuple.getT1().size());
            model.addAttribute("productCount", tuple.getT2().size());
            model.addAttribute("orderCount", tuple.getT3().size());
            return "index";
        });
    }

    @GetMapping("/sellers")
    public Mono<String> sellersPage(Model model) {
        return sellerService.getAllSellers().collectList().map(sellers -> {
            model.addAttribute("sellers", sellers);
            model.addAttribute("newSeller", new Seller());
            return "sellers";
        });
    }

    @PostMapping("/sellers/add")
    public Mono<String> addSeller(@ModelAttribute Seller seller) {
        return sellerService.createSeller(seller).thenReturn("redirect:/sellers");
    }

    @GetMapping("/products")
    public Mono<String> productsPage(Model model) {
        return productService.getAllProducts().collectList().map(products -> {
            model.addAttribute("products", products);
            model.addAttribute("newProduct", new Product());
            return "products";
        });
    }

    @PostMapping("/products/add")
    public Mono<String> addProduct(@ModelAttribute Product product) {
        return productService.createProduct(product).thenReturn("redirect:/products");
    }

    @GetMapping("/orders")
    public Mono<String> ordersPage(Model model) {
        return orderService.getAllOrders().collectList().map(orders -> {
            model.addAttribute("orders", orders);
            model.addAttribute("newOrder", new CustomerOrder());
            return "orders";
        });
    }

    @PostMapping("/orders/add")
    public Mono<String> addOrder(@ModelAttribute CustomerOrder order) {
        return orderService.createOrder(order).thenReturn("redirect:/orders");
    }

    @PostMapping("/orders/{orderId}/cancel")
    public Mono<String> cancelOrder(@PathVariable Long orderId) {
        return orderService.cancelOrderAndRestoreStock(orderId).thenReturn("redirect:/orders");
    }
}
