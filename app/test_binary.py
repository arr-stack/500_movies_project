
numbers = [{'id': 1, 'title': 'a'}, {'id': 2, 'title': 'Java'}, {'id': 3, 'title': 'c'}]
target = 'Java'
left = 0
right = len(numbers) - 1

while left <= right:
   middle = (left + right) // 2
   middle_item = numbers[middle]
   if middle_item['title'] == target:
       print(middle_item)
       print('Found!')
       break
   elif middle_item['title'] < target:
       left = middle + 1
   else:
       right = middle - 1
