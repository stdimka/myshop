import pytest
from shop.models import Review


@pytest.mark.django_db
class TestReview:

    def test_add_review(self, user, product):
        """Пользователь может добавить отзыв на товар."""
        review = Review.objects.create(
            user=user,
            product=product,
            rating=5,
            comment="Отлично!"
        )
        assert review.id is not None
        assert review.user == user
        assert review.product == product
        assert review.rating == 5
        assert review.comment == "Отлично!"

    def test_review_factory(self, review_factory, user, product):
        """Проверка работы фабрики отзывов."""
        review = review_factory(user=user, product=product, rating=4, comment="Хорошо")
        assert review.rating == 4
        assert review.comment == "Хорошо"
        assert review.user == user
        assert review.product == product

    def test_reviews_are_listed_correctly(self, product, review_factory, user):
        """Проверка получения всех отзывов по товару."""
        review1 = review_factory(user=user, product=product, rating=5)
        review2 = review_factory(user=user, product=product, rating=4)

        reviews = Review.objects.filter(product=product)
        assert len(reviews) == 2
        assert review1 in reviews
        assert review2 in reviews

    def test_review_links_to_product_and_user(self, review):
        """Проверка связи отзыва с пользователем и товаром."""
        assert review.user is not None
        assert review.product is not None
