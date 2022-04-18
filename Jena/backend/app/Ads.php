<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Ads extends Model
{
  protected $fillable = ['title', 'url','description','user_id','ad_image','type','extra','add_fb_id','camp','sponser','status'];
  
  /**
   * Get all category ID for each ads
   */
  public function category()
  {
    return $this->hasMany('App\AdsCategory', 'ads_id', 'id');
  }

  /**
   * Get all category ID for each ads
   */
  public function notes()
  {
    // return $this->hasOne('App\AdsCategory', 'ads_id', 'id');
    return $this->hasOne('App\Note', 'ads_id', 'id');
  }
}
