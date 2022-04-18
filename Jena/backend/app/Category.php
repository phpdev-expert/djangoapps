<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Category extends Model
{
  protected $fillable = ['user_id', 'title'];
  
  /**
   * Get the user of category.
   */
  public function user()
  {
      return $this->belongsTo('App\User')->withDefault();
  }

  /**
   * Get Category Name
   */
  public static function fetchCategoryName($catIds = array())
  {
    return Category::whereIn('id', $catIds)->get();
  }

}
