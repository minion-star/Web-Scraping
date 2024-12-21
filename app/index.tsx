import React, { useState, useEffect } from 'react';
import { View, Text, Image, FlatList, StyleSheet } from 'react-native';

// Define the Book type
type Book = {
  Category: string;
  ID: string;
  Title: string;
  Price: string;
  "Image URL": string;
};

export default function Index() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    try {
      const response = await fetch('http://10.0.2.2:5000/scrape');
      const data = await response.json();
      setBooks(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={books}
        keyExtractor={(item) => item.ID}
        
        renderItem={({ item }) => (
          <View style={styles.bookItem}>
            <Image
              source={{ uri: `http://books.toscrape.com/${item["Image URL"]}` }}
              style={styles.bookImage}
            />
            <View style={styles.bookDetails}>
              <Text style={styles.bookTitle}>{item.Title}</Text>
              <Text>{item.Price}</Text>
            </View>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  bookItem: {
    flexDirection: 'row',
    marginBottom: 20,
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  bookImage: {
    width: 100,
    height: 150,
    marginRight: 10,
  },
  bookDetails: {
    justifyContent: 'center',
  },
  bookTitle: {
    fontWeight: 'bold',
  },
});
