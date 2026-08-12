/**
 * 장바구니 아이템 수량 업데이트 
 */
export function updateCartItemsQty(cartItems, cid, type) {
    return cartItems.map((item) => 
                item.cid === cid ?
                    type === '+'? {...item, qty: item.qty+1}   
                                : item.qty > 1 ? {...item, qty: item.qty-1} : item
                :   item );
}

/**
 * 상품 총 금액 구하기
 */
export function getTotalPrice(products, items) {
    return (items ?? []).reduce((total, item) => {
        const product = products.find(product => item.pid === product.pid);
        return total + (item.qty * product.price);
    }, 0);    
}

/**
 * 상품리스트에서 이미지, 상품명, 가격 --> 장바구니 리스트에 추가
 */
export function cartItemsAddInfo(products, items) {
    return items.map((item)=> { 
        const product = products.find((product) => item.pid === product.pid);
        return {
            ...item,
            image: product.image,
            name: product.name,
            info: product.info,
            price: product.price
        };
    }); 
}


/**
 * 장바구니 수량 증가 체크 함수
 */
export function cartItemsCheck(prevItems, cartItem) { //{pid:1, size:'XS', qty:1}
    //존재여부 체크
    //cartItems =[{pid:3, size:M, qty:5}, {pid:4, size:M, qty:1}]
    //cartItem = {pid:3, size: M, qty:1}
    const existItem = prevItems.find((item) => 
                            item.pid === cartItem.pid && item.size === cartItem.size);

    if(existItem) { //존재하면 map으로 순회하면서 pid, size가 동일한 item에 qty +1 증가
        return prevItems.map((item) =>  //map은 새로운 배열 반환
        item.pid === cartItem.pid && item.size === cartItem.size
            ? { ...item, qty: item.qty + 1 } 
            : item
        );
    } else {        
        const cid = Math.floor(Math.random() * 10000000);
        return [...prevItems, {...cartItem, cid:cid } ];  //존재하지 않으면 새로운 item 추가
    }
}



